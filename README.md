# unos Multilingual TTS & Zero-Shot Voice Cloning

A fully offline, open-source multilingual Text-to-Speech (TTS) and Zero-shot Voice Cloning application powered by:
1. **Meta's MMS-TTS (Massively Multilingual Speech)** models for standard TTS.
2. **Coqui's XTTS-v2** model for zero-shot voice cloning.

Supports **14 languages** for standard TTS, and **English & Hindi** for zero-shot voice cloning with precise speed control. Unlike gated models, Meta MMS-TTS is completely public and requires no login or Hugging Face authentication tokens.

---

## Features

| Feature | Details |
|---|---|
| **Standard TTS Languages** | 14 languages: English, Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Assamese, Dogri, Urdu |
| **Voice Cloning Languages** | English & Hindi (using Coqui XTTS-v2) |
| **Voice Control** | Speed slider (Turtle/Rabbit speed factor: 0.25x – 2.0x) |
| **Speaker Style (Standard)** | Single fixed high-quality voice per language |
| **Zero-Shot Voice Cloning** | Clones any speaker's voice using a 3–5 second reference WAV recording |
| **Export** | WAV (always) · MP3 (with ffmpeg) |
| **Inference** | CUDA GPU (fast) or CPU (slower fallback) |
| **Offline** | ✅ Works fully offline after first model download |
| **API** | ❌ No paid/commercial APIs used, no login tokens needed |

---

## Requirements

- Python 3.10 or newer
- pip
- *(Optional but strongly recommended)* a CUDA-capable NVIDIA GPU
- *(Optional, for MP3 export)* [ffmpeg](https://ffmpeg.org/) in your PATH

---

## Setup Instructions

### 1 – Clone / download the project

```bash
cd voice-model-tts
```

### 2 – Create a virtual environment (recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 – Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4 – (Optional) Install ffmpeg for MP3 export

- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/) and add to PATH, or use `winget install ffmpeg`.
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg` / `sudo dnf install ffmpeg`

---

## Running the Application

```bash
python app.py
```

The Gradio UI will open automatically in your browser at:
```
http://127.0.0.1:7860
```

---

## How Model Weights Are Downloaded & Cached

On the first run of a feature, the model weights are automatically downloaded from Hugging Face Hub to your local cache:

*   **MMS-TTS checkpoints** (~150-200 MB per language): Downloaded anonymously and cached in:
    *   Windows: `C:\Users\<you>\.cache\huggingface\hub\`
    *   macOS / Linux: `~/.cache/huggingface/hub/`
*   **XTTS-v2 model weights** (~1.8 GB): Downloaded on first use of the Voice Cloning tab and cached in:
    *   Windows: `C:\Users\<you>\AppData\Local\tts\tts_models--multilingual--multi-dataset--xtts_v2`
    *   macOS / Linux: `~/.local/share/tts/tts_models--multilingual--multi-dataset--xtts_v2`

No login or Hugging Face tokens are required. The Coqui license agreement is accepted programmatically via the backend.

---

## Why Kannada & Telugu Voice Cloning is Unsupported

AI4Bharat's IndicF5 voice cloning model was evaluated for Kannada and Telugu cloning support, but was rejected because:
1. It is gated on Hugging Face and requires manual repository access approval.
2. It requires `huggingface_hub.login()` or setting `HF_TOKEN` environment variables.

This violates our goal of having a completely open, zero-auth, offline-first system. Zero-shot voice cloning is therefore restricted to **English** and **Hindi** via XTTS-v2, which has a public license and does not require registration/authentication.

---

## Project Structure

```
voice-model-tts/
├── app.py              ← Gradio UI (entry point)
├── tts_engine.py       ← MMS-TTS & XTTS-v2 model loading + inference logic
├── requirements.txt    ← Python dependencies
├── README.md           ← This file
└── report/
    ├── README.md       ← Metadata about the project report
    └── report.md       ← Full project evaluation report
```

---

## Known Limitations

1. **No Emotion / Tone Control (MMS-TTS)**: The standard TTS models use fixed-style checkpoints that do not support dynamic prompt conditioning.
2. **Single Voice Per Language (MMS-TTS)**: Each standard TTS language checkpoint is trained on a single speaker.
3. **Hardware Latency for XTTS-v2**: Zero-shot voice cloning using XTTS-v2 is computationally expensive. Run on an NVIDIA GPU via CUDA for the best real-time performance. On a CPU, inference may take up to 3–4x the audio duration.

---

## License

This project uses the following open-source components:

- **Meta MMS-TTS** – [CC BY-NC 4.0](https://github.com/facebookresearch/fairseq/tree/main/examples/mms)
- **Coqui XTTS-v2** – [Coqui Public Model License 1.0.0 (CPML)](https://coqui.ai/cpml.txt)
- **Gradio** – [Apache 2.0](https://github.com/gradio-app/gradio)
- **PyTorch** – [BSD](https://github.com/pytorch/pytorch/blob/main/LICENSE)
