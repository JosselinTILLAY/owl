from config import (
    ELEVEN_LABS_MODEL_ID, 
    ELEVEN_LABS_VOICE_ID_ALEX, 
    ELEVEN_LABS_VOICE_ID_JAMIE
)

# Voice Mappings for Different Personas
# Persona names must match those in the podcast scripts/prompts
VOCAL_CONFIG = {
    "openai": {
        "model": "tts-1",
        "voices": {
            "Alex": "nova",       # Vibrant, energetic female
            "Jamie": "onyx",      # Clear, authoritative male
            "Narrator": "alloy",  # Balanced, standard voice
        },
        "pause_duration_ms": 400
    },
    "elevenlabs": {
        "model_id": ELEVEN_LABS_MODEL_ID,
        "voices": {
            "Alex": ELEVEN_LABS_VOICE_ID_ALEX,
            "Jamie": ELEVEN_LABS_VOICE_ID_JAMIE,
            "Narrator": "IKne3meq5aSn9XLyUdCD"
        },
        "default_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        },
        "persona_settings": {
            "Alex": {
                "stability": 0.4,       # More expressive, dynamic
                "similarity_boost": 0.9, # Higher voice clarity/fidelity
                "style": 0.0,
                "use_speaker_boost": True
            },
            "Jamie": {
                "stability": 0.6,       # More steady, authoritative
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        },
        "pause_duration_ms": 300
    }
}
