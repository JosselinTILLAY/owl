import os
import httpx
import uuid
from typing import Literal, List
from pydub import AudioSegment
from config import (
    client, logger, PODCASTS_DIR, ELEVEN_LABS_API_KEY,
    FFMPEG_PATH, FFPROBE_PATH, OPENAI_MODEL_ID, PROMPTS
)
from vocal_config import VOCAL_CONFIG
from services.music_service import generate_background_music
from models import PodcastScript

# Configure pydub to find ffmpeg
if os.path.exists(FFMPEG_PATH):
    AudioSegment.converter = FFMPEG_PATH
if os.path.exists(FFPROBE_PATH):
    AudioSegment.ffprobe = FFPROBE_PATH

def generate_podcast_script_content(
    text_content: str, 
    mode: Literal["solo", "duo"] = "duo"
) -> PodcastScript:
    """Generates a podcast script from text content using OpenAI."""
    
    try:
        system_prompt = PROMPTS['podcast'][mode]['system']
        user_prompt = PROMPTS['podcast']['user_template'].format(text=text_content[:15000])

        response = client.beta.chat.completions.parse(
            model=OPENAI_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=PodcastScript
        )
        return response.choices[0].message.parsed
    except Exception as e:
        logger.error(f"Failed to generate podcast script: {str(e)}")
        raise e

async def synthesize_audio_openai(
    script: PodcastScript, 
    output_path: str
):
    """Synthesizes multi-voice audio using OpenAI TTS with individual line stitching."""
    # Mapping personas from vocal config
    voices = VOCAL_CONFIG["openai"]["voices"]
    pause_ms = VOCAL_CONFIG["openai"]["pause_duration_ms"]

    temp_files = []
    try:
        combined_audio = AudioSegment.empty()
        
        async with httpx.AsyncClient() as http_client:
            for i, line in enumerate(script.lines):
                voice = voices.get(line.speaker, voices["Narrator"])
                logger.info(f"Generating OpenAI audio for {line.speaker} (line {i+1}) using {voice}...")
                
                try:
                    # Using the direct OpenAI sync client but keeping it compatible with our async flow
                    response = client.audio.speech.create(
                        model=VOCAL_CONFIG["openai"]["model"],
                        voice=voice,
                        input=line.content
                    )
                    
                    temp_filename = f"temp_oa_{uuid.uuid4()}.mp3"
                    temp_path = os.path.join(PODCASTS_DIR, temp_filename)
                    response.stream_to_file(temp_path)
                    temp_files.append(temp_path)
                    
                    # Load and stitch
                    segment = AudioSegment.from_mp3(temp_path)
                    combined_audio += segment
                    combined_audio += AudioSegment.silent(duration=pause_ms) # Natural pause
                    logger.info(f"Appended {line.speaker}'s line. Current duration: {len(combined_audio)}ms")
                    
                except Exception as e:
                    logger.error(f"OpenAI line generation failed for {line.speaker}: {str(e)}")
                    continue

        if len(combined_audio) > 0:
            combined_audio.export(output_path, format="mp3")
            logger.info(f"Successfully stitched OpenAI podcast (Final Size: {os.path.getsize(output_path)} bytes)")
        else:
            logger.error("OpenAI combined audio is empty!")
            raise Exception("Generated audio is empty.")

    finally:
        # Cleanup temp files
        for f in temp_files:
            try: os.remove(f)
            except: pass

async def synthesize_audio_elevenlabs(
    script: PodcastScript, 
    output_path: str, 
    mode: Literal["solo", "duo"] = "duo"
):
    """Synthesizes audio using ElevenLabs API with multi-voice stitching."""
    if not ELEVEN_LABS_API_KEY:
        raise Exception("ElevenLabs API key is missing. Please set it in your .env file.")

    # Voice mappings and settings from vocal config
    voices = VOCAL_CONFIG["elevenlabs"]["voices"]
    default_settings = VOCAL_CONFIG["elevenlabs"]["default_settings"]
    persona_settings = VOCAL_CONFIG["elevenlabs"].get("persona_settings", {})
    pause_ms = VOCAL_CONFIG["elevenlabs"]["pause_duration_ms"]

    temp_files = []
    try:
        combined_audio = AudioSegment.empty()
        
        async with httpx.AsyncClient() as http_client:
            for i, line in enumerate(script.lines):
                voice_id = voices.get(line.speaker, voices["Narrator"])
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": ELEVEN_LABS_API_KEY
                }
                # Get persona-specific settings or fallback to default
                current_voice_settings = persona_settings.get(line.speaker, default_settings)

                data = {
                    "text": line.content,
                    "model_id": VOCAL_CONFIG["elevenlabs"]["model_id"],
                    "voice_settings": current_voice_settings
                }

                logger.info(f"Generating audio for {line.speaker} (line {i+1})...")
                response = await http_client.post(url, json=data, headers=headers)
                
                if response.status_code != 200:
                    logger.error(f"ElevenLabs line generation failed ({response.status_code}): {response.text}")
                    continue
                
                content_size = len(response.content)
                logger.info(f"Received {content_size} bytes for {line.speaker}")
                
                if content_size < 100:
                    logger.warning(f"Audio content too small for {line.speaker}, skipping.")
                    continue

                temp_filename = f"temp_{uuid.uuid4()}.mp3"
                temp_path = os.path.join(PODCASTS_DIR, temp_filename)
                with open(temp_path, "wb") as f:
                    f.write(response.content)
                
                actual_size = os.path.getsize(temp_path)
                logger.info(f"Saved temp file {temp_path} (size: {actual_size} bytes)")
                
                temp_files.append(temp_path)
                
                try:
                    segment = AudioSegment.from_mp3(temp_path)
                    combined_audio += segment
                    combined_audio += AudioSegment.silent(duration=pause_ms)
                    logger.info(f"Successfully appended {line.speaker}'s line. Current duration: {len(combined_audio)}ms")
                except Exception as segment_err:
                    logger.error(f"Failed to process audio segment for {line.speaker}: {str(segment_err)}")
        
        if len(combined_audio) > 0:
            # --- Enhancement: Background Music Mixing ---
            try:
                logger.info("🎸 Generating background music for the podcast...")
                music_prompt = "lo-fi hip hop study beats, calm, ambient, academic atmosphere"
                # Duration should match or be slightly longer than the audio
                music_path = generate_background_music(music_prompt, duration_ms=len(combined_audio) + 5000)
                
                if music_path and os.path.exists(music_path):
                    bg_music = AudioSegment.from_mp3(music_path)
                    # Lower volume of music significantly (-25dB)
                    bg_music = bg_music - 25 
                    # Mix music and voice
                    combined_audio = bg_music.overlay(combined_audio)
                    logger.info("✅ Background music mixed successfully.")
                    # Cleanup music file
                    try: os.remove(music_path)
                    except: pass
            except Exception as music_err:
                logger.warning(f"⚠️ Music mixing failed (continuing with voice only): {str(music_err)}")

            combined_audio.export(output_path, format="mp3")
            logger.info(f"Successfully stitched {len(temp_files)} lines into {output_path} (Final Size: {os.path.getsize(output_path)} bytes)")
        else:
            logger.error("Combined audio is empty after processing all lines!")
            raise Exception("Generated audio is empty.")

    finally:
        # Cleanup temp files
        for f in temp_files:
            try: os.remove(f)
            except: pass
