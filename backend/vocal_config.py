from config import (
    ELEVEN_LABS_MODEL_ID,
    ELEVEN_LABS_VOICE_ID_ALEX,
    ELEVEN_LABS_VOICE_ID_JAMIE
)

# Voice Mappings for Owl & Billie personas
# Owl = prof (voix homme), Billie = étudiante (voix femme)
VOCAL_CONFIG = {
    "openai": {
        "model": "tts-1-hd",
        "voices": {
            "Owl": "onyx",        # Voix homme, prof charismatique
            "Billie": "nova",     # Voix femme, étudiante spontanée
            "Alex": "onyx",       # Legacy fallback
            "Jamie": "nova",      # Legacy fallback
            "Narrator": "alloy",
        },
        "speed": 1.1,
        "pause_duration_ms": 150
    },
    "elevenlabs": {
        "model_id": ELEVEN_LABS_MODEL_ID,
        "voices": {
            "Owl": ELEVEN_LABS_VOICE_ID_JAMIE,      # Voix homme
            "Billie": ELEVEN_LABS_VOICE_ID_ALEX,     # Voix femme
            "Alex": ELEVEN_LABS_VOICE_ID_JAMIE,      # Legacy fallback
            "Jamie": ELEVEN_LABS_VOICE_ID_ALEX,      # Legacy fallback
            "Narrator": "IKne3meq5aSn9XLyUdCD",
        },
        "default_settings": {
            "stability": 0.3,
            "similarity_boost": 0.65,
            "style": 0.7,
            "use_speaker_boost": True
        },
        "persona_settings": {
            "Owl": {
                "stability": 0.3,
                "similarity_boost": 0.65,
                "style": 0.7,
                "use_speaker_boost": True
            },
            "Billie": {
                "stability": 0.25,
                "similarity_boost": 0.6,
                "style": 0.85,
                "use_speaker_boost": True
            }
        },
        "pause_duration_ms": 150,
        "batch_size": 5
    }
}
