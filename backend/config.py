import os
import logging
import shutil
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("owl-backend")

# Load environment variables
load_dotenv(override=True)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG_ID = os.getenv("OPENAI_ORG_ID")

if OPENAI_API_KEY:
    logger.info(f"OpenAI API Key loaded (length: {len(OPENAI_API_KEY)})")
else:
    logger.warning("OPENAI_API_KEY not found in environment!")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    organization=OPENAI_ORG_ID
)

# Platform Configuration
MOODLE_URL = os.getenv("MOODLE_URL", "http://localhost:8000")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8001))

# AI Versions & Models
OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-5.4")

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
ELEVEN_LABS_MODEL_ID = os.getenv("ELEVEN_LABS_MODEL_ID", "eleven_multilingual_v2")
ELEVEN_LABS_VOICE_ID_ALEX = os.getenv("ELEVEN_LABS_VOICE_ID_ALEX", "Xb7hH8MSUJpSbSDYk0k2")
ELEVEN_LABS_VOICE_ID_JAMIE = os.getenv("ELEVEN_LABS_VOICE_ID_JAMIE", "TX3LPaxmHKxFdv7VOQHJ")

# System Binary Paths (Auto-detect FFmpeg)
FFMPEG_PATH = os.getenv("FFMPEG_PATH") or shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
FFPROBE_PATH = os.getenv("FFPROBE_PATH") or shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"

if ELEVEN_LABS_API_KEY:
    logger.info(f"ElevenLabs API Key loaded (suffix: ...{ELEVEN_LABS_API_KEY[-4:] if len(ELEVEN_LABS_API_KEY) > 4 else 'SHORT'})")
else:
    logger.warning("ELEVEN_LABS_API_KEY not found!")

# Storage Configuration
STATIC_DIR = "static"
PODCASTS_DIR = os.path.join(STATIC_DIR, "podcasts")

# Ensure directories exist
os.makedirs(PODCASTS_DIR, exist_ok=True)
