from config import client, logger, OPENAI_MODEL_ID
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
    logger.info(f"⚡ GPT-5.4 Summarization requested. Input text length: {text_len} chars.")
    
    if text_len < 50:
        logger.warning("Extracted text is very short. Summarization might fail.")

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ID,
            reasoning_effort="none",
            messages=[
                {"role": "system", "content": (
                    "You are a professional educational summarizer. Analyze the FULL text and produce a professional summary. "
                    "You MUST speak and output ONLY in ENGLISH. For ALL math formulas, use professional LaTeX notation strictly wrapped in \\( ... \\) for inline and \\[ ... \\] for block math."
                )},
                {"role": "user", "content": f"Please summarize this entire course content in ENGLISH:\n\n{text}"}
            ],
            max_completion_tokens=2500
        )
        content = response.choices[0].message.content
        if not content:
            logger.error("OpenAI returned empty content for summary.")
            return ""
            
        logger.info(f"Summarization successful. Response length: {len(content)} chars.")
        return content
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise e

async def generate_exercises(text: str) -> str:
    """Generates interactive QCM in ENGLISH."""
    logger.info("⚡ GPT-5.4 Exercises requested (English results).")
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ID,
            reasoning_effort="none",
            messages=[
                {"role": "system", "content": (
                    "You are an educational designer generating interactive QCM exercises. You MUST speak and output ONLY in ENGLISH. "
                    "For ALL math formulas, use professional LaTeX notation strictly wrapped in \\( ... \\) for inline and \\[ ... \\] for block math."
                )},
                {"role": "user", "content": (
                    f"Based on this content, generate 3 multiple choice questions (MCQ) in ENGLISH. "
                    f"Structure each question with a header '### Question X', four options A, B, C, D, "
                    f"and end with '> **Answer: X**' followed by a short explanation in ENGLISH. "
                    f"Use the whole text :\n\n{text}"
                )}
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
        system_prompt = (
            "You are a cool and funny educational TikTok/Reels content creator. "
            "Your style is that of a chill student: use expressions like 'bro', 'straight fire', 'insane', 'let's go'. "
            "Summarize a concept from the text into a super fast and engaging script in ENGLISH. "
            "Script duration: 45-55 seconds. "
            "IMPORTANT: Use ONLY information from the text. You MUST speak ONLY in ENGLISH."
        )
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Transform this course into a fire script for a Short in ENGLISH:\n\n{text[:10000]}"}
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
