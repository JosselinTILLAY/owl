import uuid
import shutil
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models import PodcastResponse
from config import logger, PODCASTS_DIR, STATIC_DIR
from utils import extract_text_from_pdf
from services.podcast_service import (
    generate_podcast_script_content, 
    synthesize_audio_openai, 
    synthesize_audio_elevenlabs
)

router = APIRouter(tags=["Podcast Generation"])

@router.post("/upload-pdf")
async def upload_pdf_file(file: UploadFile = File(...)):
    """Uploads a PDF and extracts its text for processing."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(STATIC_DIR, f"{uuid.uuid4()}.pdf")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        text = extract_text_from_pdf(file_path)
        return {"text": text, "filename": file.filename}
    except Exception as e:
        logger.error(f"PDF extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

@router.post("/generate-podcast", response_model=PodcastResponse)
async def generate_podcast_audio(
    text: str = Form(...), 
    mode: str = Form("duo"), 
    provider: str = Form("openai")
):
    """Generates a podcast MP3 from the provided text."""
    logger.info(f"Podcast generation requested: mode={mode}, provider={provider}")
    
    try:
        # 1. Generate Script
        script = generate_podcast_script_content(text, mode=mode)
        
        # 2. Synthesize Audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"podcast_{timestamp}.mp3"
        output_path = os.path.join(PODCASTS_DIR, filename)
        
        if provider == "elevenlabs":
            await synthesize_audio_elevenlabs(script, output_path, mode=mode)
        else:
            await synthesize_audio_openai(script, output_path)
        
        audio_url = f"/static/podcasts/{filename}"
        return PodcastResponse(
            title=script.title,
            audio_url=audio_url,
            script=script.lines,
            duration_estimate="2 minutes"
        )
    except Exception as e:
        logger.error(f"Podcast generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
