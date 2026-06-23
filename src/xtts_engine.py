"""
xtts_engine.py
──────────────
Lazy-loading and inference wrapper for Coqui's XTTS-v2 voice cloning model.
"""

import logging
import os
import torch

logger = logging.getLogger('xtts_engine')

class XTTSEngine:
    """
    Wraps Coqui's XTTS-v2 for zero-shot voice cloning.
    """
    def __init__(self, device=None) -> None:
        self.xtts_model = None
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = torch.device(device)
        logger.info('👥 XTTSEngine initialized on device: %s', self.device)

    def clone_voice(
        self,
        text: str,
        speaker_wav: str,
        language: str = 'English',
        speed: float = 1.0,
        output_path: str = None
    ) -> tuple[str, int]:
        """
        Perform voice cloning using XTTS-v2 and return the output file path and sample rate.
        """
        if language not in ('English', 'Hindi'):
            raise ValueError(f"Voice cloning is not supported for '{language}'. Only English and Hindi are supported.")

        if not speaker_wav or not os.path.exists(speaker_wav):
            raise ValueError('Reference speaker WAV file is missing or invalid.')

        if not text or not text.strip():
            raise ValueError('Input text is empty. Please enter some text.')

        if self.xtts_model is None:
            logger.info('⏳ Loading XTTS-v2 model (downloads ~1.8 GB on first run)...')
            os.environ['COQUI_TOS_AGREED'] = '1'
            from TTS.api import TTS
            self.xtts_model = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
            if torch.cuda.is_available():
                self.xtts_model.to(self.device)
            logger.info('✅ XTTS-v2 model loaded successfully.')

        lang_code = 'en' if language == 'English' else 'hi'
        logger.info('🎙️ Performing voice cloning | lang=%s | ref=%s | speed=%.2f', language, speaker_wav, speed)

        if not output_path:
            import tempfile
            import time
            output_path = os.path.join(
                tempfile.gettempdir(),
                f"xtts_output_{int(time.time())}.wav"
            )

        self.xtts_model.tts_to_file(
            text=text.strip(),
            speaker_wav=speaker_wav,
            language=lang_code,
            file_path=output_path,
            speed=speed
        )

        return output_path, 24000
