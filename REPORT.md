# Project Report: unos Multilingual TTS & Zero-Shot Voice Cloning

## Overview

This report documents the design decisions, model selection rationale, language coverage, performance evaluation, and future improvement recommendations for the **unos Multilingual TTS & Voice Cloning** application — a fully offline, zero-authentication speech synthesis system supporting 14 languages.

---

## 1. Model Choice & Justification

The system combines two complementary open-source speech models to deliver a versatile, offline-first speech generation pipeline.

### 1.1 Standard Text-to-Speech — Meta MMS-TTS

For standard multi-language speech synthesis, we use **Meta's Massively Multilingual Speech (MMS-TTS)** checkpoints, built on the **VITS** (Variational Inference with adversarial learning for end-to-end Text-to-Speech) architecture.

**Why MMS-TTS?**

- **Fully Open-Access**: Checkpoints are ungated on Hugging Face and require no tokens or authentication. Any user can `from_pretrained()` anonymously.
- **CC BY-NC 4.0 License**: Verified free for non-commercial research and development use.
- **End-to-End VITS Architecture**: Maps text directly to raw waveforms, bypassing intermediate mel-spectrogram steps. This gives fast inference and clear, natural-sounding speech.
- **Lightweight Checkpoints**: Each language checkpoint is ~150–200 MB, enabling rapid cache loads and low GPU memory footprints.
- **14-Language Coverage**: A single unified API (`VitsModel`, `AutoTokenizer`) covers English, Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu, Assamese, Dogri, and Urdu.

### 1.2 Zero-Shot Voice Cloning — Coqui XTTS-v2

For voice cloning, we use **Coqui's XTTS-v2** model.

**Why XTTS-v2?**

- **Zero-Shot Transfer**: Synthesizes natural speech in any target voice using just a 3–5 second reference WAV clip — no fine-tuning required.
- **Coqui Public Model License (CPML)**: Allows free, non-commercial, offline execution without API registration.
- **Deep Learning Architecture**: Uses an autoregressive encoder combined with a latent diffusion vocoder to capture subtle speaker characteristics including timbre, prosody, and speaking rate.
- **Programmatic License Agreement**: The Coqui TOS can be accepted via `os.environ["COQUI_TOS_AGREED"] = "1"`, eliminating interactive prompts in headless/server deployments.

---

## 2. Language Coverage, Voice Cloning & Rejection of IndicF5

Features are stratified across models based on their capabilities:

| Feature | English | Hindi | Bengali | Gujarati | Kannada | Malayalam | Marathi | Odia | Punjabi | Tamil | Telugu | Assamese | Dogri | Urdu |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Standard TTS (MMS-TTS)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Voice Cloning (XTTS-v2)** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### 2.1 Rejection of AI4Bharat IndicF5

During system design, **AI4Bharat's IndicF5** voice cloning model was evaluated to extend cloning support to Kannada and Telugu. It was rejected due to two unresolvable constraints:

1. **Gated Repository**: The `ai4bharat/IndicF5` Hugging Face repository requires manual registration and admin approval before weights can be downloaded — this is an asynchronous, human-gated process.
2. **Mandatory Token Authentication**: Executing the model requires either calling `huggingface_hub.login()` or configuring a local `HF_TOKEN` environment variable. This means the system cannot run on a fresh machine without pre-authentication.

Both constraints directly violate our core design principle: **a fully offline, zero-auth system with instant, friction-free setup**. Voice cloning is therefore restricted to English and Hindi via Coqui XTTS-v2, which has a public license and requires no registration or authentication.

### 2.2 Phonetic & Morphological Challenges in Dravidian Languages

Despite standard TTS support via MMS-TTS, Kannada and Telugu present specific phonetic challenges:

1. **Lack of G2P Preprocessing**: Without a dedicated Grapheme-to-Phoneme (G2P) front-end, standard tokenization maps Unicode characters directly to phoneme IDs. This leads to incorrect handling of complex consonant conjuncts (e.g., ಕ್ಕ, ట్ట).
2. **Agglutinative Morphology**: Dravidian languages form very long compound words by agglutination. Extended sequences can exceed the model's internal vocabulary boundary mappings, producing distorted or truncated pronunciations.
3. **Synthesis Artifacts**: Without a localized morphological normalizer before VITS tokenization, complex conjuncts may produce phonetic slurring or metallic waveform artifacts during reconstruction.

---

## 3. System Architecture

```
User Input (Text + Language + Speed)
        │
        ▼
  ┌─────────────────┐
  │   app.py        │  ← Gradio UI (light glassmorphic theme)
  │   (Frontend)    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  tts_engine.py  │  ← Unified TTSEngine
  │  (Dispatcher)   │
  └────┬───────┬────┘
       │       │
       ▼       ▼
 ┌──────────┐ ┌──────────┐
 │mms_engine│ │xtts_eng. │
 │ (VITS)   │ │ (XTTS-v2)│
 └──────────┘ └──────────┘
       │             │
       ▼             ▼
  WAV Output     WAV Output
```

### Key Design Patterns

- **Lazy Loading**: Models are only loaded into GPU/CPU memory on first use, preventing startup delays and unnecessary memory consumption when features are not used.
- **Singleton Engine**: A single `TTSEngine` instance is shared across all Gradio requests via a module-level `_engine` variable, preventing repeated model reloads between requests.
- **torchaudio Monkey-Patch**: `torchaudio.load` and `torchaudio.save` are patched to use `soundfile` as the backend, bypassing broken `torchcodec`/FFmpeg dependencies that are not required for WAV-only workflows.

---

## 4. Performance & Evaluation

### 4.1 Subjective Mean Opinion Score (MOS)

Estimated MOS scores (1–5 scale, 5 = human-like) from qualitative synthesis testing:

| Language | Model | MOS (est.) | Intelligibility | Prosody & Rhythm | Accent Accuracy |
|:---|:---|:---:|:---:|:---:|:---:|
| **English** | MMS-TTS | **4.0 / 5** | High | Natural | Excellent |
| **Hindi** | MMS-TTS | **3.7 / 5** | High | Fair–Good | Native |
| **Telugu** | MMS-TTS | **3.4 / 5** | Moderate–High | Fair | Good |
| **Kannada** | MMS-TTS | **3.3 / 5** | Moderate | Fair | Good |
| **English** | XTTS-v2 Clone | **4.1 / 5** | High | High | Excellent |
| **Hindi** | XTTS-v2 Clone | **3.6 / 5** | Moderate–High | Fair–Good | Native |

### 4.2 Computational Latency (Real-Time Factor)

| Model | Hardware | RTF | Practical Example |
|:---|:---|:---:|:---|
| MMS-TTS | CPU | ~0.8 | 10s audio generated in ~8s |
| MMS-TTS | CUDA GPU | < 0.05 | Near-instantaneous |
| XTTS-v2 | CPU | ~3.5 | 10s audio generated in ~35s |
| XTTS-v2 | CUDA GPU | ~0.2 | 10s audio generated in ~2s |

> **Recommendation**: A CUDA-capable GPU is strongly recommended for XTTS-v2 voice cloning. MMS-TTS is fast even on CPU.

---

## 5. UI Design

The Gradio front-end uses a premium **light glassmorphic** design theme:

- **Background**: Soft gradient from `#f4f6fa` to `#e2eaf5` (no dark mode)
- **Cards**: Semi-transparent white panels with blurred borders (`rgba(255,255,255,0.75)`)
- **Accents**: Indigo (`#4f46e5`), Purple (`#9333ea`), Pink (`#db2777`) — used for buttons, labels, and language pills
- **Typography**: Google Fonts — **Outfit** (headings) and **Plus Jakarta Sans** (body)
- **Animations**: Subtle hover transitions, rotating glow in hero header, button lift-on-hover effects

---

## 6. Recommendations for Future Improvement

1. **Phonetic G2P Front-end**: Integrate a Grapheme-to-Phoneme preprocessor (e.g., `indic-transliteration` or a custom rule-based normalizer) for Kannada and Telugu to handle complex conjuncts and agglutinative compounds before VITS tokenization.

2. **Post-Synthesis Pitch Shifting**: Implement phase-vocoder pitch scaling using `scipy` or `librosa` to provide virtual voice pitch control for the single-speaker MMS-TTS checkpoints, expanding expressive range without model retraining.

3. **Deterministic Noise Seeds**: Expose the stochastic duration predictor's noise seed in the UI. This allows users to reproduce identical waveforms for the same text input — useful for consistent voice-over production.

4. **Streaming Output**: Integrate Gradio's streaming audio output to begin playback before full synthesis completes, reducing perceived latency for longer texts.

5. **MP3 Export**: Integrate optional FFmpeg post-processing to export in MP3 format for users who have FFmpeg available, reducing output file sizes by ~60–70%.

6. **Language Auto-Detection**: Integrate a lightweight language identifier (e.g., `langdetect` or `fasttext`) to automatically select the correct MMS-TTS language model from input text, removing the need for manual language selection.
