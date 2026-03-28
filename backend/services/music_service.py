import os
from config import client, logger

def generate_background_music(prompt: str, duration_ms: int = 30000) -> str:
    """
    Generates a background music track using ElevenLabs Music API.
    Returns the path to the generated MP3 file.
    """
    logger.info(f"🎵 Generating music with prompt: {prompt}")
    try:
        # ElevenLabs Music (text-to-music) API
        # The prompt should describe the style/mood
        audio_iterator = client.music.compose(
            prompt=prompt,
            music_length_ms=duration_ms,
            output_format="mp3_44100_128"
        )

        music_filename = f"bg_music_{os.urandom(4).hex()}.mp3"
        music_path = os.path.join("static", "music", music_filename)
        os.makedirs(os.path.dirname(music_path), exist_ok=True)

        with open(music_path, "wb") as f:
            for chunk in audio_iterator:
                f.write(chunk)

        logger.info(f"✅ Music generated: {music_path}")
        return music_path
    except Exception as e:
        logger.error(f"❌ Music generation failed: {str(e)}")
        # Fallback: Return a silence or a placeholder if API fails
        return ""
