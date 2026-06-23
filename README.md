# unos Multilingual TTS & Zero-Shot Voice Cloning

> A fully offline, open-source multilingual Text-to-Speech and Zero-shot Voice Cloning application — no API keys, no login, no internet required after first setup.

Powered by **Meta's MMS-TTS** for standard TTS across 14 languages and **Coqui's XTTS-v2** for zero-shot voice cloning in English & Hindi.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Standard TTS Languages** | 14 languages: English, Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Assamese, Dogri, Urdu |
| **Voice Cloning Languages** | English & Hindi (zero-shot, using Coqui XTTS-v2) |
| **Speed Control** | Smooth speed slider: 0.25× (slow) → 2.0× (fast) |
| **Reference Audio** | 3–5 second WAV clip recorded via mic or uploaded |
| **Export Format** | WAV (always available) |
| **Inference Hardware** | CUDA GPU (fast) or CPU (automatic fallback) |
| **Fully Offline** | ✅ Works without internet after first model download |
| **Zero Authentication** | ❌ No API keys, HF tokens, or login required |
| **UI Theme** | Modern light glassmorphic design (Indigo/Pink/Purple accents) |

---

## 🗂️ Project Structure

```
voice-model/
├── app.py                  ← Gradio UI entry point (light glassmorphic theme)
├── tts_engine.py           ← Unified TTSEngine (delegates to MMS + XTTS)
├── download_models.py      ← Pre-download all model weights for offline use
├── requirements.txt        ← Python package dependencies
├── README.md               ← This file
├── REPORT.md               ← Full project evaluation & design report
└── src/
    ├── mms_engine.py       ← Meta MMS-TTS VITS inference wrapper
    ├── xtts_engine.py      ← Coqui XTTS-v2 voice cloning wrapper
    ├── presets.py          ← Language-to-model-ID mappings & emotion configs
    └── audio_utils.py      ← Audio processing utilities (resampling, etc.)
```

---

## ⚙️ Requirements

- Python **3.10** or newer
- `pip`
- *(Strongly recommended)* NVIDIA GPU with CUDA support
- *(Optional, for MP3 export)* [ffmpeg](https://ffmpeg.org/) in your PATH

---

## 🚀 Setup Instructions

### 1 — Clone the repository

```bash
git clone https://github.com/Haswanth1510/voice-model.git
cd voice-model
```

### 2 — Create a virtual environment *(recommended)*

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4 — *(Optional)* Pre-download all model weights for offline use

```bash
# Download English & Hindi MMS models + XTTS-v2 (default)
python download_models.py

# Download ALL 14 language MMS models + XTTS-v2
python download_models.py --all-mms

# Skip XTTS-v2 (only download MMS models)
python download_models.py --no-xtts
```

### 5 — *(Optional)* Install ffmpeg for MP3 export

| OS | Command |
|---|---|
| Windows | `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/) |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` |

---

## ▶️ Running the Application

```bash
python app.py
```

The Gradio UI opens automatically in your browser at:
```
http://127.0.0.1:7860
```

---

## 📦 How Model Weights Are Cached

Model weights are downloaded automatically on first use and cached locally — no manual setup required.

| Model | Size | Cache Location (Windows) |
|---|---|---|
| **MMS-TTS** (per language) | ~150–200 MB each | `C:\Users\<you>\.cache\huggingface\hub\` |
| **Coqui XTTS-v2** | ~1.8 GB total | `C:\Users\<you>\AppData\Local\tts\tts_models--multilingual--...` |

> On macOS/Linux, Hugging Face cache is at `~/.cache/huggingface/hub/` and Coqui at `~/.local/share/tts/`.

No login or Hugging Face tokens are required. The Coqui license agreement is accepted programmatically.

---

## ⚠️ Why Kannada & Telugu Voice Cloning is Not Supported

AI4Bharat's **IndicF5** voice cloning model was evaluated for Kannada and Telugu support, but was rejected for two reasons:

1. **Gated Repository**: `ai4bharat/IndicF5` requires manual approval on Hugging Face before download.
2. **Mandatory Token Auth**: Requires `huggingface_hub.login()` or a `HF_TOKEN` environment variable.

These requirements conflict with our core design goal: a **fully offline, zero-auth** system. Voice cloning is therefore limited to **English** and **Hindi** via Coqui XTTS-v2, which is publicly licensed and requires no authentication.

---

## ⚡ Performance Notes

| Mode | Hardware | Real-Time Factor (RTF) |
|---|---|---|
| MMS-TTS Standard | CPU | ~0.8 (10s audio in ~8s) |
| MMS-TTS Standard | CUDA GPU | < 0.05 (near-instantaneous) |
| XTTS-v2 Voice Cloning | CPU | ~3.5 (10s audio in ~35s) |
| XTTS-v2 Voice Cloning | CUDA GPU | ~0.2 (10s audio in ~2s) |

---

## 🚧 Known Limitations

1. **No Emotion / Tone Control**: MMS-TTS checkpoints are single-style and do not support prompt-conditioned emotion.
2. **Single Voice Per Language**: Each MMS-TTS language checkpoint is trained on one fixed speaker.
3. **XTTS-v2 CPU Latency**: Voice cloning on CPU is slow (~3–4× audio duration). A CUDA GPU is strongly recommended.

---

## 📄 License

| Component | License |
|---|---|
| **Meta MMS-TTS** | [CC BY-NC 4.0](https://github.com/facebookresearch/fairseq/tree/main/examples/mms) |
| **Coqui XTTS-v2** | [Coqui Public Model License 1.0.0 (CPML)](https://coqui.ai/cpml.txt) |
| **Gradio** | [Apache 2.0](https://github.com/gradio-app/gradio) |
| **PyTorch** | [BSD License](https://github.com/pytorch/pytorch/blob/main/LICENSE) |
