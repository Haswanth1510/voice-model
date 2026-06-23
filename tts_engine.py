"""
tts_engine.py
─────────────
Unified TTS Engine wrapper that delegates standard TTS to MMSEngine
and voice cloning to XTTSEngine. Includes torchaudio monkey patch.
"""

import logging
import os
import torch
import numpy as np

# --- Monkey patch torchaudio to use soundfile instead of broken torchcodec/FFmpeg ---
import torchaudio
import soundfile as sf

def patched_load(filepath, frame_offset=0, num_frames=-1, normalize=True, channels_first=True, format=None, buffer_size=4096, backend=None):
    data, samplerate = sf.read(filepath, dtype='float32')
    if frame_offset > 0:
        data = data[frame_offset:]
    if num_frames > 0:
        data = data[:num_frames]
    tensor = torch.from_numpy(data)
    if tensor.ndim == 1:
        tensor = tensor.unsqueeze(0)
    elif tensor.ndim == 2:
        if channels_first:
            tensor = tensor.T
    return tensor, samplerate

def patched_save(uri, src, sample_rate, channels_first=True, **kwargs):
    if isinstance(src, torch.Tensor):
        data = src.detach().cpu().numpy()
    else:
        data = src
    if channels_first:
        data = data.T
    sf.write(uri, data, sample_rate)

torchaudio.load = patched_load
torchaudio.save = patched_save

# Set environment variable to bypass Coqui license confirmation prompt programmatically
os.environ["COQUI_TOS_AGREED"] = "1"

from src.mms_engine import MMSEngine
from src.xtts_engine import XTTSEngine

logger = logging.getLogger('tts_engine')

class TTSEngine:
    """
    Unified engine for standard text-to-speech and zero-shot voice cloning.
    """
    def __init__(self, device=None) -> None:
        self.device = device
        self.mms = MMSEngine(device=device)
        self.xtts = XTTSEngine(device=device)

    def generate(self, text: str, language: str = 'English', speed: float = 1.0) -> tuple:
        """
        Synthesize speech using standard Meta MMS-TTS.
        """
        return self.mms.generate(text=text, language=language, speed=speed)

    def clone_voice(
        self,
        text: str,
        speaker_wav: str,
        language: str = 'English',
        speed: float = 1.0,
        output_path: str = None
    ) -> tuple:
        """
        Clone a speaker's voice using Coqui XTTS-v2.
        """
        return self.xtts.clone_voice(
            text=text,
            speaker_wav=speaker_wav,
            language=language,
            speed=speed,
            output_path=output_path
        )