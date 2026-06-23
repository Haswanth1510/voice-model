"""
presets.py
──────────
Contains language list configuration and emotion preset mapping for the TTS application.
"""

LANGUAGES = [
    'English', 'Hindi', 'Bengali', 'Gujarati', 'Kannada', 'Malayalam', 
    'Marathi', 'Odia', 'Punjabi', 'Tamil', 'Telugu', 'Assamese', 'Dogri', 'Urdu'
]

LANG_MODELS = {
    'English': 'facebook/mms-tts-eng',
    'Hindi': 'facebook/mms-tts-hin',
    'Bengali': 'facebook/mms-tts-ben',
    'Gujarati': 'facebook/mms-tts-guj',
    'Kannada': 'facebook/mms-tts-kan',
    'Malayalam': 'facebook/mms-tts-mal',
    'Marathi': 'facebook/mms-tts-mar',
    'Odia': 'facebook/mms-tts-ory',
    'Punjabi': 'facebook/mms-tts-pan',
    'Tamil': 'facebook/mms-tts-tam',
    'Telugu': 'facebook/mms-tts-tel',
    'Assamese': 'facebook/mms-tts-asm',
    'Dogri': 'facebook/mms-tts-dgo',
    'Urdu': 'facebook/mms-tts-urd-script_arabic'
}

EMOTION_PRESETS = {
    'Default': {
        'speed': 1.0,
        'pitch': 1.0,
        'volume': 1.0,
        'pause_factor': 1.0
    },
    'Happy': {
        'speed': 1.15,
        'pitch': 1.12,
        'volume': 1.05,
        'pause_factor': 0.85
    },
    'Sad': {
        'speed': 0.82,
        'pitch': 0.9,
        'volume': 0.8,
        'pause_factor': 1.3
    },
    'Angry': {
        'speed': 1.2,
        'pitch': 0.96,
        'volume': 1.2,
        'pause_factor': 0.75
    },
    'Excited': {
        'speed': 1.25,
        'pitch': 1.18,
        'volume': 1.1,
        'pause_factor': 0.7
    },
    'Whisper': {
        'speed': 0.9,
        'pitch': 0.94,
        'volume': 0.45,
        'pause_factor': 1.4
    }
}