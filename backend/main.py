import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("owl-backend")

# Load environment variables
load_dotenv()

app = FastAPI(title="Moodle OWL AI Backend (Minimal)")

@app.get("/")
async def root():
    return {"message": "Moodle OWL AI Backend is running. Visit /docs for API documentation."}

# OpenAI Configuration
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Unhandled error during {request.method} {request.url.path}: {str(e)}", exc_info=True)
        raise e

class Feature(BaseModel):
    id: str
    name: str
    description: str

class TextRequest(BaseModel):
    content: str

@app.get("/features", response_model=List[Feature])
async def get_features():
    """Lists all available AI features of the OWL block."""
    return [
        Feature(id="summarize", name="Chapter Summary", description="Generate summaries for your course materials."),
        Feature(id="exercises", name="Interactive Exercises", description="Generate QCM and dynamic exercises."),
        Feature(id="podcast", name="Audio Synthesis", description="Generate a podcast summary of your PDF."),
        Feature(id="shorts", name="Micro-Learning Shorts", description="Generate scripts for short video formats.")
    ]

@app.post("/summarize")
async def summarize(request: TextRequest):
    """Generates a structured chapter summary using OpenAI."""
    logger.info("Summarization requested.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional educational content summarizer."},
                {"role": "user", "content": f"Please summarize the following course content into a clean, structured chapter summary for students:\n\n{request.content}"}
            ]
        )
        logger.info("Summarization successful.")
        return {"summary": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-exercises")
async def generate_exercises(request: TextRequest):
    """Generates interactive QCM and activities."""
    logger.info("Exercise generation requested.")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an educational designer generating interactive QCM exercises."},
                {"role": "user", "content": f"Based on this content, generate 3 multiple choice questions with answers:\n\n{request.content}"}
            ]
        )
        logger.info("Exercise generation successful.")
        return {"exercises": response.choices[0].message.content}
    except Exception as e:
        logger.error(f"Exercise generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-podcast")
async def generate_podcast(request: TextRequest):
    """Generates metadata and text for an audio synthesis of the content."""
    # Note: In a real implementation, you might use OpenAI's TTS API for actual audio.
    return {
        "script": f"Welcome to the synthesis podcast. Today we are discussing key points from: {request.content[:200]}...",
        "audio_url": "/api/static/podcast_placeholder.mp3"
    }

@app.post("/generate-shorts")
async def generate_shorts(request: TextRequest):
    """Generates a script and metadata for short-format educational clips."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media educational content creator. Create a high-energy, vertical video script (under 60s) for a complex topic."},
                {"role": "user", "content": f"Transform this topic into a 'Short' or 'Reel' script:\n\n{request.content}"}
            ]
        )
        return {
            "script": response.choices[0].message.content,
            "format": "9:16",
            "duration_estimate": "55s"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
