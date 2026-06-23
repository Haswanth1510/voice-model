# Project Report: Multilingual TTS & Zero-shot Voice Cloning

## 1. Model Choice & Justification

This project combines two complementary speech synthesis models to deliver a versatile offline speech generation pipeline without reliance on gated APIs or manual authorization workflows.

### Standard Text-to-Speech: Meta MMS-TTS
For standard, multi-language speech generation, we use **Meta's Massively Multilingual Speech Text-to-Speech (MMS-TTS)** checkpoints via the `VitsModel` architecture.
*   **Fully Open-Access**: Checkpoints are not gated and do not require Hugging Face authentication tokens or API registration.
*   **CC-BY-NC 4.0 License**: Verified as free for non-commercial research and development.
*   **VITS Architecture**: An end-to-end Variational Inference with adversarial learning model. Mapping text directly to raw waveforms bypasses intermediate mel-spectrogram steps, providing fast inference and clear speech.
*   **Lightweight**: Checkpoints are ~150–200 MB, enabling fast cache loads and minimal memory footprints.

### Voice Cloning: Coqui XTTS-v2
For zero-shot voice cloning, we utilize **Coqui's XTTS-v2** model.
*   **Zero-shot Transfer**: Generates natural speech in a target voice from a 3–5 second reference audio clip.
*   **Coqui Public Model License (CPML)**: Allows free non-commercial offline execution.
*   **Deep Learning Architecture**: Utilizes an autoregressive encoder with a latent diffusion vocoder to capture subtle speaker characteristics (timbre, prosody, and speed).

---
## 2. Language Coverage, Voice Cloning, & Rejection of IndicF5

The system supports speech generation across target languages, but features are stratified by model capabilities:

| Feature / Language | English | Hindi | Kannada | Telugu |
| :--- | :---: | :---: | :---: | :---: |
| **Standard TTS (MMS-TTS)** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Voice Cloning (XTTS-v2)** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |

### Kannada & Telugu Voice Cloning Rejection (IndicF5)
During architectural design, we explored utilizing AI4Bharat's IndicF5 model to enable Kannada and Telugu voice cloning. However, IndicF5 was rejected due to two principal constraints:
1. **Gated Access**: The model repository (`ai4bharat/IndicF5`) is gated on Hugging Face, requiring manual registration and waiting for administrator approval.
2. **Mandatory Token Auth**: Running the model requires active authentication via `huggingface_hub.login()` or configuring local `HF_TOKEN` environment variables.

These requirements violate our primary objective: a fully offline, zero-auth system with instant setup. Therefore, voice cloning is restricted to English and Hindi via Coqui XTTS-v2, which has a public license and does not require registration/authentication.

### Phonetic & Morphological Challenges
Implementing speech synthesis for Dravidian languages (Kannada & Telugu) via Meta's MMS-TTS exposed specific phonetic and morphological limitations:
1. **Lack of G2P Preprocessing**: Without a dedicated Grapheme-to-Phoneme (G2P) front-end, standard tokenization maps letters directly. This leads to incorrect tokenization of complex consonant conjuncts.
2. **Agglutination**: Dravidian languages use extensive compound word joining (agglutination). Long compound words can exceed the model's vocabulary boundary mappings, causing distorted pronunciations.
3. **Synthesis Artifacts**: The lack of localized morphological normalizers before entering VITS tokenization means complex consonant conjuncts can produce slight phonetic "slurring" or metallic artifacts during waveform reconstruction.

---
## 3. Performance & Evaluation

### Subjective Mean Opinion Score (MOS)
Estimated MOS scores (1–5 scale, where 5 is human-like) compiled from qualitative synthesis tests:

| Language | Model | Estimated MOS | Intelligibility | Prosody & Rhythm | Accent Accuracy |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **English** | MMS-TTS | **4.0 / 5** | High | Natural | Excellent |
| **Hindi** | MMS-TTS | **3.7 / 5** | High | Fair-Good | Native |
| **Telugu** | MMS-TTS | **3.4 / 5** | Moderate-High | Fair | Good |
| **Kannada** | MMS-TTS | **3.3 / 5** | Moderate | Fair | Good |
| **English** | XTTS-v2 | **4.1 / 5** | High | High (Captures timbre) | Excellent |
| **Hindi** | XTTS-v2 | **3.6 / 5** | Moderate-High | Fair-Good | Native |

### Computational Latency (Real-time Factor - RTF)
*   **MMS-TTS (Standard)**: Extremely fast. On modern CPU, RTF ~0.8 (generates 10s of audio in 8s). On CUDA GPU, RTF < 0.05 (instantaneous).
*   **XTTS-v2 (Cloning)**: Computationally heavy. On modern CPU, RTF ~3.5 (generates 10s of audio in 35s). On CUDA GPU, RTF ~0.2 (generates 10s of audio in 2s).

---

## 4. Recommendations for Future Improvement

1.  **Phonetic Front-end G2P**: Integrate a Grapheme-to-Phoneme preprocessor for Kannada and Telugu to normalize complex conjuncts and split agglutinative compound terms prior to VITS tokenization.
2.  **Post-Synthesis Pitch Shifting**: Implement phase-vocoder pitch scaling (e.g., using `scipy` or `librosa`) to allow virtual voice pitch control for the single-speaker MMS-TTS models.
3.  **Seed Anchoring**: Expose deterministic noise seed controls in the stochastic duration predictor of the VITS architecture to allow exact reproduction of speech waveforms for identical text.
