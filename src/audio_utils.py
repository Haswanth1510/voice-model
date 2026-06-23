"""
audio_utils.py
──────────────
Provides digital signal processing (DSP) utilities for standard audio waveforms:
- Phase-vocoder-based speed changing
- Resampling-based pitch shifting
- Chunk-based pause/silence scaling
- Peak amplitude normalization
- WAV and MP3 export helpers
"""

import os
import numpy as np
import scipy.signal
import soundfile as sf
from pydub import AudioSegment

def normalize_audio(waveform: np.ndarray) -> np.ndarray:
    """Normalize peak amplitude to -0.95 to 0.95 to prevent clipping."""
    max_val = np.max(np.abs(waveform))
    if max_val > 0:
        return (waveform / max_val) * 0.95
    return waveform

def change_speed(waveform: np.ndarray, speed_factor: float, sr: int = 24000) -> np.ndarray:
    """
    Stretch audio speed using a phase vocoder to preserve original pitch.
    """
    if np.isclose(speed_factor, 1.0) or speed_factor <= 0.05:
        return waveform

    n_fft = 1024
    hop_length = 256

    _, _, spec = scipy.signal.stft(
        waveform,
        fs=sr,
        nperseg=n_fft,
        noverlap=n_fft - hop_length
    )

    num_bins, num_frames = spec.shape
    new_num_frames = int(np.ceil(num_frames / speed_factor))

    phi_advance = np.linspace(0, np.pi * hop_length, num_bins)
    time_steps = np.arange(new_num_frames) * speed_factor

    stretched_spec = np.zeros((num_bins, new_num_frames), dtype=np.complex128)

    phase_acc = np.angle(spec[:, 0])
    stretched_spec[:, 0] = spec[:, 0]

    for t in range(1, new_num_frames):
        pos = time_steps[t]
        idx1 = int(np.floor(pos))
        idx2 = min(idx1 + 1, num_frames - 1)
        alpha = pos - idx1

        mag = (1.0 - alpha) * np.abs(spec[:, idx1]) + alpha * np.abs(spec[:, idx2])
        dp = np.angle(spec[:, idx2]) - np.angle(spec[:, idx1])
        dp_unwrapped = dp - phi_advance
        dp_unwrapped = dp_unwrapped - 2.0 * np.pi * np.round(dp_unwrapped / (2.0 * np.pi))
        dp_final = dp_unwrapped + phi_advance

        phase_acc += dp_final
        stretched_spec[:, t] = mag * np.exp(1j * phase_acc)

    _, reconstructed = scipy.signal.istft(
        stretched_spec,
        fs=sr,
        nperseg=n_fft,
        noverlap=n_fft - hop_length
    )

    return reconstructed

def change_pitch(waveform: np.ndarray, pitch_factor: float, sr: int = 24000) -> np.ndarray:
    """
    Shift pitch without changing duration using a combination of resampling and phase vocoder.
    """
    if np.isclose(pitch_factor, 1.0) or pitch_factor <= 0.05:
        return waveform

    num_samples = len(waveform)
    new_num_samples = int(num_samples / pitch_factor)

    resampled = scipy.signal.resample(waveform, new_num_samples)
    stretched = change_speed(resampled, 1.0 / pitch_factor, sr)
    return stretched

def adjust_pauses(waveform: np.ndarray, pause_factor: float, sr: int = 24000) -> np.ndarray:
    """
    Adjust duration of silent regions chunk-by-chunk using basic energy thresholding.
    """
    if np.isclose(pause_factor, 1.0) or pause_factor < 0:
        return waveform

    chunk_size = int(0.025 * sr)
    num_chunks = len(waveform) // chunk_size

    if num_chunks == 0:
        return waveform

    chunks = [waveform[i * chunk_size : (i + 1) * chunk_size] for i in range(num_chunks)]
    rem = waveform[num_chunks * chunk_size :]

    processed_chunks = []
    silence_threshold = 0.005

    for chunk in chunks:
        rms = np.sqrt(np.mean(chunk ** 2))
        if rms < silence_threshold:
            repeats = int(round(pause_factor))
            if repeats <= 0:
                continue
            for _ in range(repeats):
                processed_chunks.append(chunk)
        else:
            processed_chunks.append(chunk)

    if processed_chunks:
        output = np.concatenate(processed_chunks)
        if len(rem) > 0:
            output = np.concatenate([output, rem])
        return output
    else:
        return rem

def export_wav(waveform: np.ndarray, sr: int, filepath: str) -> None:
    """Export waveform to WAV format."""
    sf.write(filepath, waveform, sr)

def export_mp3(waveform: np.ndarray, sr: int, filepath: str) -> bool:
    """
    Export waveform to MP3 format using pydub.
    Returns True if successful, False if it failed due to ffmpeg dependency.
    """
    try:
        int_data = (waveform * 32767).astype(np.int16)
        audio_segment = AudioSegment(
            int_data.tobytes(),
            frame_rate=sr,
            sample_width=2,
            channels=1
        )
        audio_segment.export(filepath, format='mp3')
        return True
    except Exception as exc:
        print('[WARN] MP3 export failed, ffmpeg might be missing: ' + str(exc))
        return False
