from config import (
    ELEVEN_LABS_MODEL_ID,
    ELEVEN_LABS_VOICE_ID_OWL,
    ELEVEN_LABS_VOICE_ID_BILLIE,
    MISTRAL_VOICE_ID_MAN,
    MISTRAL_VOICE_ID_WOMAN
)

# Voice Mappings — Owl (Antoine) & Billie (Koraly)
VOCAL_CONFIG = {
    "openai": {
        "model": "tts-1-hd",
        "voices": {
            "Owl": "onyx",        # Voix homme, prof charismatique
            "Billie": "nova",     # Voix femme, étudiante spontanée
            "Narrator": "alloy",
        },
        "speed": 1.1,
        "pause_duration_ms": 150
    },
    "elevenlabs": {
        "model_id": ELEVEN_LABS_MODEL_ID,
        "voices": {
            "Owl": ELEVEN_LABS_VOICE_ID_OWL,        # Antoine — Warm and fluid
            "Billie": ELEVEN_LABS_VOICE_ID_BILLIE,   # Koraly — Virtual assistant
            "Narrator": ELEVEN_LABS_VOICE_ID_OWL,
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
    },
    "voxtral": {
        "voices": {
            "Owl": MISTRAL_VOICE_ID_MAN,
            "Billie": MISTRAL_VOICE_ID_WOMAN,
            "Narrator": MISTRAL_VOICE_ID_MAN
        },
        "pause_duration_ms": 150
    }
}
