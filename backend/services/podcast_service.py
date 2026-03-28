import os
import httpx
import uuid
from typing import Literal, List
from pydub import AudioSegment
from config import (
    client, logger, PODCASTS_DIR, ELEVEN_LABS_API_KEY,
    ELEVEN_LABS_MODEL_ID, ELEVEN_LABS_VOICE_ID_ALEX, ELEVEN_LABS_VOICE_ID_JAMIE,
    FFMPEG_PATH, FFPROBE_PATH, OPENAI_MODEL_ID
)
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
    
    if mode == "solo":
        system_prompt = (
            "You are a dynamic educational content creator. "
            "Your goal is to transform the provided text into a 2-minute 'Crash Course' style solo narration in ENGLISH. "
            "IMPORTANT: Use ONLY information from the text provided. "
            "Stay cool, fast, and engaging for students. "
            "Speak directly to the audience ('you'). The tone should be accessible and modern. "
            "Format your response as JSON with a title and a list of lines (speaker 'Narrator')."
        )
    else:
        system_prompt = (
            "You are two students, Alex and Jamie, discussing a course. "
            "Alex is super energetic and curious, Jamie is more calm and pedagogical. "
            "Your goal is to discuss the provided text in a 3-minute 'Coffee Break' conversation format in ENGLISH. "
            "IMPORTANT: Develop the concepts well. Be pedagogical. "
            "Generate about 15 to 25 lines of dialogue to cover all content. "
            "Use ONLY information from the text provided. "
            "The tone should be 'cool student': accessible, with natural student-like expressions, "
            "while remaining very clear on technical concepts. "
            "Use natural reactions ('oh really?', 'exactly!', 'I see'). "
            "Format your response as JSON with a list of lines (Alex and Jamie)."
        )

    try:
        response = client.beta.chat.completions.parse(
            model=OPENAI_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voici le contenu à transformer en podcast étudiant :\n\n{text_content[:15000]}"}
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
    # Mapping student personas to OpenAI voices
    voices = {
        "Alex": "nova",   # Vibrant, energetic female
        "Jamie": "onyx",  # Clear, authoritative male
        "Narrator": "alloy"
    }

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
                        model="tts-1",
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
                    combined_audio += AudioSegment.silent(duration=400) # Natural pause
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

    # Voice IDs (from environment)
    voices = {
        "Alex": ELEVEN_LABS_VOICE_ID_ALEX,
        "Jamie": ELEVEN_LABS_VOICE_ID_JAMIE,
        "Narrator": "IKne3meq5aSn9XLyUdCD" # Default fallback
    }

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
                data = {
                    "text": line.content,
                    "model_id": ELEVEN_LABS_MODEL_ID,
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
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
                    combined_audio += AudioSegment.silent(duration=300)
                    logger.info(f"Successfully appended {line.speaker}'s line. Current duration: {len(combined_audio)}ms")
                except Exception as segment_err:
                    logger.error(f"Failed to process audio segment for {line.speaker}: {str(segment_err)}")
        
        if len(combined_audio) > 0:
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
