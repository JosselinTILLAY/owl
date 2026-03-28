import os
import subprocess
from config import client, logger, OPENAI_MODEL_ID, FFMPEG_PATH, STATIC_DIR
from services.music_service import generate_background_music

def generate_short_video(audio_path: str, script_title: str, music_prompt: str = "chill lo-fi hip hop") -> str:
    """
    Synthesizes a short video (MP4) from an audio track and a permanent background image.
    Uses ElevenLabs for music and FFmpeg for assembly.
    """
    logger.info(f"🎬 Starting video synthesis for: {script_title}")
    
    try:
        # 1. Use Permanent Background Image
        image_path = os.path.join(STATIC_DIR, "images", "studio_bg.png")
        if not os.path.exists(image_path):
            logger.warning("⚠️ Background image not found, check path.")

        # 2. Get Background Music (ElevenLabs)
        music_path = generate_background_music(music_prompt, duration_ms=60000)

        # 3. Assemble with FFmpeg
        video_filename = f"short_{os.urandom(4).hex()}.mp4"
        video_path = os.path.join(STATIC_DIR, "videos", video_filename)
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        # FFmpeg command:
        # - Loop the image
        # - Layer the voice (audio_path)
        # - Layer the music (music_path) with ducking (-15dB)
        # - Sync everything to voice length
        cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1", "-i", image_path,
            "-i", audio_path,
            "-i", music_path,
            "-filter_complex", "[2:a]volume=0.15[bg];[1:a][bg]amix=inputs=2:duration=first",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-shortest",
            video_path
        ]

        logger.info(f"🎞️ Running FFmpeg encoding: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        logger.info(f"✅ Video synthesis complete: {video_path}")
        return video_path

    except Exception as e:
        logger.error(f"❌ Video synthesis failed: {str(e)}")
        raise e
