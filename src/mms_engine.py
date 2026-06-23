"""
mms_engine.py
─────────────
Lazy-loading and inference wrapper for Meta's Massively Multilingual Speech (MMS-TTS) VITS models.
"""

import logging
import torch
import numpy as np
from src.presets import LANG_MODELS

logger = logging.getLogger('mms_engine')

class MMSEngine:
    """
    Wraps the VITS models for standard TTS standard synthesis.
    """
    def __init__(self, device=None) -> None:
        self.models = {}
        self.tokenizers = {}
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = torch.device(device)
        logger.info('🌐 MMSEngine initialized on device: %s', self.device)

    def _get_model_and_tokenizer(self, language: str):
        """Lazy load the MMS-TTS model and tokenizer for a specific language."""
        if language not in LANG_MODELS:
            raise ValueError(f'Unsupported language: {language}')

        if language not in self.models:
            model_id = LANG_MODELS[language]
            logger.info("⏳ Loading MMS-TTS model for %s from '%s'...", language, model_id)

            from transformers import VitsModel, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = VitsModel.from_pretrained(model_id)

            model.to(self.device)
            model.eval()

            self.models[language] = model
            self.tokenizers[language] = tokenizer
            logger.info('✅ Loaded %s model successfully.', language)

        return self.models[language], self.tokenizers[language]

    def generate(
        self,
        text: str,
        language: str = 'English',
        speed: float = 1.0,
        noise_scale: float = 0.667,
        noise_scale_w: float = 0.8
    ) -> tuple[np.ndarray, int]:
        """
        Run MMS-TTS inference and return the raw waveform as a float32 numpy array and its sample rate.
        """
        if not text or not text.strip():
            raise ValueError('Input text is empty. Please enter some text.')

        model, tokenizer = self._get_model_and_tokenizer(language)

        logger.info('🎙️ MMS-TTS generating speech | lang=%s | speed=%.2f | noise=%.3f', language, speed, noise_scale)

        inputs = tokenizer(text.strip(), return_tensors='pt').to(self.device)

        model.speaking_rate = speed

        if hasattr(model.config, 'noise_scale'):
            model.config.noise_scale = noise_scale

        if hasattr(model.config, 'noise_scale_w'):
            model.config.noise_scale_w = noise_scale_w

        with torch.no_grad():
            outputs = model(**inputs)

        waveform = outputs.waveform[0].cpu().numpy()
        sample_rate = model.config.sampling_rate

        return waveform, sample_rate
