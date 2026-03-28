import os
from fastapi import APIRouter, HTTPException, Form
from services.ai_service import generate_shorts_script
from services.podcast_service import synthesize_audio_elevenlabs
from services.video_service import generate_short_video
from config import logger

router = APIRouter(tags=["Video Features"])

@router.post("/generate-short-video")
async def generate_short_video_endpoint(
    text: str = Form(...),
    music_prompt: str = Form("chill lo-fi hip hop")
):
    """Generates a funny, high-energy educational short video (MP4)."""
    logger.info("🎬 Video generation request received.")
    try:
        # 1. Generate Funny Script
        script_data = await generate_shorts_script(text)
        script_text = script_data["script"]
        
        # 2. Synthesize High-Energy Audio
        # Parse the script into lines for the Duo synthesizer
        # (Assuming the script is already formatted or we treat it as Alex's narration for simplicity)
        # Actually, let's treat it as a single high-energy narration for the 'Short' format
        # or parse it if it has 'Alex:' / 'Jamie:' tags.
        from models import Line
        lines = []
        for l in script_text.split('\n'):
            if ':' in l:
                speaker, content = l.split(':', 1)
                lines.append(Line(speaker=speaker.strip(), content=content.strip()))
            elif l.strip():
                lines.append(Line(speaker="Alex", content=l.strip()))

        audio_res = await synthesize_audio_elevenlabs(lines)
        audio_path = audio_res["audio_path"]

        # 3. Assemble Video
        video_path = generate_short_video(
            audio_path=audio_path,
            script_title="Short Éducatif: " + script_text[:30],
            music_prompt=music_prompt
        )

        relative_video_path = "/" + video_path
        return {
            "video_url": relative_video_path,
            "script": script_text,
            "audio_url": audio_res["audio_url"]
        }

    except Exception as e:
        logger.error(f"❌ Video generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
