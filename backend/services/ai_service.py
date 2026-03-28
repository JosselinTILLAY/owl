from config import client, logger, OPENAI_MODEL_ID, PROMPTS
from models import Feature

async def get_available_features():
    """Returns the list of available AI features."""
    return [
        Feature(id="summarize", name="Course Summary", description="Generate summaries for your course materials."),
        Feature(id="exercises", name="MCQ Exercises", description="Generate dynamic multiple-choice questions."),
        Feature(id="podcast", name="Audio Synthesis", description="Generate a podcast summary of your PDF."),
        Feature(id="shorts", name="Education Shorts", description="Generate scripts for short video formats.")
    ]

async def generate_summary(text: str) -> str:
    """Generates a structured chapter summary in ENGLISH."""
    text_len = len(text)
    # Truncate to first 70k chars to ensure stable summarization for massive files (100k+ tokens)
    text_to_process = text[:70000]
    logger.info(f"⚡ {OPENAI_MODEL_ID.upper()} Summarization requested. Input text length: {text_len} chars (truncated to {len(text_to_process)}).")
    
    if text_len < 10:
        return "The PDF seems to be empty or an image-only scan. Please use a document with selectable text."

    # Standard models like gpt-4o handle dense materials smoothly without special reasoning tiers.
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ID,
            messages=[
                {"role": "system", "content": PROMPTS['summarize']['system']},
                {"role": "user", "content": PROMPTS['summarize']['user'].replace("{text}", text_to_process)}
            ],
            max_completion_tokens=4000
        )
        
        # Check for model refusal
        if hasattr(response.choices[0].message, 'refusal') and response.choices[0].message.refusal:
            logger.error(f"❌ Model refusal detected: {response.choices[0].message.refusal}")
            return f"The AI refused to generate a summary for this content: {response.choices[0].message.refusal}"

        content = response.choices[0].message.content
        if not content or content.strip() == "":
            logger.error(f"❌ OpenAI ({OPENAI_MODEL_ID}) returned empty content for summary.")
            return "The AI was unable to generate a summary. The document content might be too complex or restricted."
            
        logger.info(f"Summarization successful. Response length: {len(content)} chars.")
        return content
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise e

async def generate_exercises(text: str) -> str:
    """Generates interactive QCM in ENGLISH."""
    logger.info(f"⚡ {OPENAI_MODEL_ID.upper()} Exercises requested (English results).")
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ID,
            messages=[
                {"role": "system", "content": PROMPTS['exercises']['system']},
                {"role": "user", "content": PROMPTS['exercises']['user'].replace("{text}", text)}
            ]
        )
        logger.info("Exercise generation successful.")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Exercise generation failed: {str(e)}")
        raise e

async def generate_shorts_script(text: str) -> dict:
    """Generates a funny, high-energy script for short-format educational clips in ENGLISH."""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ID,
            messages=[
                {"role": "system", "content": PROMPTS['shorts']['system']},
                {"role": "user", "content": PROMPTS['shorts']['user'].replace("{text}", text[:10000])}
            ]
        )
        return {
            "script": response.choices[0].message.content,
            "format": "9:16",
            "duration_estimate": "50s",
            "tone": "funny-chill"
        }
    except Exception as e:
        logger.error(f"Shorts generation failed: {str(e)}")
        raise e

async def generate_music_prompt(text: str) -> str:
    """Extracts a dynamic musical style prompt from the provided text using AI."""
    logger.info("⚡ AI Dynamic Music Style extraction requested.")
    try:
        # Use first 5k chars for prompt generation to capture enough context
        content_sample = text[:5000]
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ID,
            messages=[
                {"role": "system", "content": PROMPTS['music_style']['system']},
                {"role": "user", "content": PROMPTS['music_style']['user'].replace("{text}", content_sample)}
            ]
        )
        style = response.choices[0].message.content.strip()
        logger.info(f"✅ Dynamic style extracted: {style}")
        return style
    except Exception as e:
        logger.error(f"❌ Dynamic style extraction failed: {str(e)}")
        return "chill lo-fi hip hop, focused, academic" # Fallback
