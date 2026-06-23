"""
app.py
──────
Modernized Gradio front-end for the multilingual Meta MMS-TTS & XTTS-v2 Voice Cloning application.
Lacks MP3 dependency and runs fully offline with a sleek light-glass design.
"""

import logging
import os
import shutil
import tempfile
import time
from pathlib import Path

import gradio as gr
import soundfile as sf

from tts_engine import TTSEngine

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("app")

# ── Temp directory for audio output ──────────────────────────────────────────
OUTPUT_DIR = Path(tempfile.gettempdir()) / "indic_tts_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Lazy model load (engine initialised on first generation request) ───────────
_engine: TTSEngine | None = None

def get_engine() -> TTSEngine:
    """Return singleton TTSEngine, creating it on first call."""
    global _engine
    if _engine is None:
        logger.info("Initialising TTS engine …")
        _engine = TTSEngine()
        logger.info("TTS engine ready ✓")
    return _engine

LANGUAGES = [
    "English", "Hindi", "Bengali", "Gujarati", "Kannada",
    "Malayalam", "Marathi", "Odia", "Punjabi", "Tamil",
    "Telugu", "Assamese", "Dogri", "Urdu"
]

SAMPLE_TEXTS: dict[str, str] = {
    "English":   "Hello! Welcome to the unos multilingual text-to-speech system. I hope you enjoy exploring different voices and emotions.",
    "Hindi":     "नमस्ते! इस बहुभाषी टेक्स्ट-टू-स्पीच सिस्टम में आपका स्वागत है। कृपया विभिन्न भाषाओं और भावों का अनुभव करें।",
    "Bengali":   "হ্যালো! এই বহুভাষিক টেক্সট-টু-স্পিচ সিস্টেমে আপনাকে স্বাগতম। বিভিন্ন ভাষা এবং আবেগ অন্বেষণ করুন।",
    "Gujarati":  "નમસ્તે! આ બહુભાષી ટેક્સ્ટ-ટુ-સ્પીચ સિસ્ટમમાં આપનું સ્વાગત છે। વિવિધ ભાષાઓ અને ભાવનાઓ અન્વેષણ કરો.",
    "Kannada":   "ನಮಸ್ಕಾರ! ಈ ಬಹುಭಾಷಾ ಪಠ್ಯ-ಭಾಷಣ ವ್ಯವಸ್ಥೆಗೆ ಸ್ವಾಗತ. ದಯವಿಟ್ಟು विभिन्न ಭಾಷೆಗಳು ಮತ್ತು ಭಾವನೆಗಳನ್ನು ಅನ್ವೇಷಿಸಿ.",
    "Malayalam": "ഹലോ! ഈ ബടുത്തുഭാഷാ ടെക്സ്റ്റ്-ടു-സ്പീച്ച് സിസ്റ്റത്തിലേക്ക് സ്വാഗതം. വിവിധ ഭാഷകളും വികാരങ്ങളും പര്യവേક્ષണം ചെയ്യുക.",
    "Marathi":   "नमस्कार! या बहुभाषिक टेक्स्ट-टू-स्पीच प्रणालीमध्ये आपले स्वागत आहे. विविध भाषा आणि भावनांचा अनुभव घ्या.",
    "Odia":      "ନମସ୍କାର! ଏହି ବହୁଭାଷିକ ଟେକ୍ସ୍ଟ-ଟୁ-ସ୍ପିଚ୍ ସିଷ୍ଟମ୍‌କୁ ସ୍ୱାଗତ। ବିଗୁଣ୍ଡା ଭାଷା ଏବଂ ଭାବନା ଅନ୍ୱେଷଣ କରନ୍ତು।",
    "Punjabi":   "ਸਤਿ ਸ੍ਰੀ ਅਕาล! ਇਸ ਬਹੁਭਾਸ਼ਾਈ ਟੈਕਸਟ-ਟੂ-ਸਪੀਚ ਪ੍ਰਣਾਲੀ ਵਿੱਚ ਤੁਹਾਡਾ ਸੁਆਗਤ ਹੈ। ਵੱਖ-ਵੱਖ ਭਾਵਨਾਵਾਂ ਦੀ ਖੋਜ ਕਰੋ।",
    "Tamil":     "வணக்கம்! இந்த பன்மொழி உரை-பேச்சு அமைப்பிற்கு வரவேற்கிறோம். பல்வேறு உணர்வுகளை ஆராயுங்கள்.",
    "Telugu":    "నమస్కారం! ఈ బహుభాషా టెక్స్ట్-టు-స్పీచ్ వ్యవస్థకు సంప్రదించండి. దయచేసి विभिन्न భావాలను అన్వేషించండి.",
    "Assamese":  "নমস্কাৰ! এই বহুভাষিক পাঠ্য-বাক্ ব্যৱস্থালৈ আপোনাক স্বাগতম। বিভিন্ন আৱেগ অন্বেষণ কৰক।",
    "Dogri":     "नमस्कार! इस बहुभाशाई टेक्सट-टू-स्पीच प्रणाली च तुआढ़ा स्वागत ऐ। बक्ख-बक्ख भाशावां दी खोज करो।",
    "Urdu":      "خوش آمدید! اس کثیر لسانی ٹیکسٹ ٹو اسپیچ سسٹم میں آپ کا استقبال ہے۔ مختلف جذبات کو دریافت کریں۔",
}


# ─────────────────────────────────────────────────────────────────────────────
# Generation Callback for MMS-TTS
# ─────────────────────────────────────────────────────────────────────────────
def generate_speech(
    text: str,
    language: str,
    speed: float,
) -> tuple:
    """
    Called by Gradio when the user clicks 'Generate Speech' in the Standard TTS tab.

    Returns
    -------
    (audio_output, wav_download_path, status_message)
    """
    if not text or not text.strip():
        return (None, None, "⚠️ Please enter some text before generating speech.")

    try:
        eng = get_engine()
        
        # Perform TTS generation (returns raw numpy waveform and sample rate)
        waveform, sample_rate = eng.generate(
            text=text,
            language=language,
            speed=speed,
        )

        # Save to temp WAV file
        wav_path = OUTPUT_DIR / f"tts_output_{int(time.time())}.wav"
        sf.write(str(wav_path), waveform, sample_rate)
        logger.info("💾 Saved WAV → %s", wav_path)

        status = (
            f"✅ Speech generated successfully! "
            f"Sample rate: {sample_rate} Hz · Language: {language} · "
            f"Speed: {speed:.2f}x"
        )
        return str(wav_path), str(wav_path), status

    except ValueError as ve:
        return None, None, f"⚠️ Validation error: {ve}"
    except Exception as exc:
        logger.exception("Unexpected error during generation")
        return None, None, f"❌ Generation failed: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Voice Cloning Callback for XTTS-v2
# ─────────────────────────────────────────────────────────────────────────────
def clone_voice_speech(
    text: str,
    language: str,
    speaker_wav: str,
    speed: float,
) -> tuple:
    """
    Called by Gradio when the user clicks 'Generate Cloned Speech' in the Voice Cloning tab.

    Returns
    -------
    (audio_output, wav_download_path, status_message)
    """
    if not text or not text.strip():
        return (None, None, "⚠️ Please enter some text before generating speech.")
    if not speaker_wav:
        return (None, None, "⚠️ Please record or upload a reference speaker WAV file.")

    try:
        eng = get_engine()
        
        # Enforce language constraints for voice cloning
        if language not in ["English", "Hindi"]:
            raise ValueError(f"Voice cloning is not supported for '{language}'. Only English and Hindi are supported.")

        # Generate voice clone
        wav_path, sample_rate = eng.clone_voice(
            text=text,
            speaker_wav=speaker_wav,
            language=language,
            speed=speed,
        )

        status = (
            f"✅ Voice cloned successfully! "
            f"Sample rate: {sample_rate} Hz · Language: {language} · "
            f"Speed: {speed:.2f}x"
        )
        return str(wav_path), str(wav_path), status

    except ValueError as ve:
        return None, None, f"⚠️ Validation error: {ve}"
    except Exception as exc:
        logger.exception("Unexpected error during voice cloning")
        return None, None, f"❌ Voice cloning failed: {exc}"


def load_sample_text(language: str) -> str:
    """Fill the text box with a sample sentence for the chosen language."""
    return SAMPLE_TEXTS.get(language, "")


# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

/* Global resets & scrollbars */
body, .gradio-container {
    font-family: 'Plus Jakarta Sans', 'Outfit', 'Inter', sans-serif !important;
    background: linear-gradient(135deg, #f4f6fa 0%, #e2eaf5 100%) !important;
    color: #334155 !important;
}

/* Light Glassmorphism Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.01);
}
::-webkit-scrollbar-thumb {
    background: rgba(15, 23, 42, 0.08);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.35);
}

/* ── Hero header ── */
.hero-header {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(241, 245, 249, 0.65) 100%) !important;
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(15, 23, 42, 0.06) !important;
    border-radius: 24px !important;
    padding: 48px 32px 36px !important;
    text-align: center;
    margin-bottom: 24px !important;
    box-shadow: 0 15px 35px rgba(99, 102, 241, 0.04) !important;
    position: relative;
    overflow: hidden;
}

.hero-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at center, rgba(99, 102, 241, 0.12) 0%, transparent 60%);
    pointer-events: none;
    animation: rotateGlow 20s linear infinite;
}

@keyframes rotateGlow {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.hero-title {
    font-family: 'Outfit', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    background: linear-gradient(135deg, #4f46e5 0%, #9333ea 50%, #db2777 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin: 0 0 12px !important;
}

.hero-sub {
    color: #475569 !important;
    font-size: 1.1rem !important;
    line-height: 1.6 !important;
    max-width: 700px;
    margin: 0 auto !important;
}

/* ── Panel Cards (glassmorphism effect) ── */
.panel-card {
    background: rgba(255, 255, 255, 0.75) !important;
    border: 1px solid rgba(15, 23, 42, 0.06) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 20px !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.02) !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.panel-card:hover {
    border-color: rgba(99, 102, 241, 0.25) !important;
    box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.06) !important;
}

.section-label {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #4f46e5 !important;
    margin-bottom: 16px !important;
    border-left: 3px solid #db2777;
    padding-left: 10px !important;
}

/* ── Custom Buttons ── */
#gen-btn {
    background: linear-gradient(135deg, #4f46e5 0%, #9333ea 100%) !important;
    border: none !important;
    color: #ffffff !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    padding: 14px 28px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

#gen-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(147, 51, 234, 0.35) !important;
    filter: brightness(1.05);
}

#gen-btn:active {
    transform: translateY(0) !important;
}

/* ── Interactive Input Fields ── */
.gr-textbox input, .gr-textbox textarea, .gr-dropdown select, .gr-file {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1px solid rgba(15, 23, 42, 0.1) !important;
    color: #1e293b !important;
    transition: all 0.2s ease !important;
    border-radius: 10px !important;
}

.gr-textbox input:focus, .gr-textbox textarea:focus, .gr-dropdown select:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15) !important;
    background: rgba(255, 255, 255, 1) !important;
}

/* Language pills */
.lang-pills {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 18px;
}

.lang-pill {
    background: rgba(99, 102, 241, 0.05) !important;
    border: 1px solid rgba(99, 102, 241, 0.15) !important;
    color: #4f46e5 !important;
    border-radius: 999px !important;
    padding: 6px 14px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}

.lang-pill:hover {
    background: rgba(236, 72, 153, 0.08) !important;
    border-color: rgba(236, 72, 153, 0.25) !important;
    color: #db2777 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(236, 72, 153, 0.1);
}

/* ── Audio Out Styling ── */
#audio-out, .gr-audio {
    background: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(15, 23, 42, 0.05) !important;
    border-radius: 14px !important;
    padding: 10px !important;
}

#status-box textarea {
    background: rgba(248, 250, 252, 0.8) !important;
    border-color: rgba(15, 23, 42, 0.05) !important;
    color: #475569 !important;
    font-family: monospace !important;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Build Gradio UI
# ─────────────────────────────────────────────────────────────────────────────
def build_ui() -> gr.Blocks:
    # Custom modern light theme configuration
    theme = gr.themes.Default(
        primary_hue="indigo",
        secondary_hue="pink",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Outfit"), "Inter", "sans-serif"],
    ).set(
        # General backgrounds & borders
        body_background_fill="linear-gradient(135deg, #f4f6fa 0%, #e2eaf5 100%)",
        block_background_fill="rgba(255, 255, 255, 0.7)",
        block_border_color="rgba(15, 23, 42, 0.08)",
        block_border_width="1px",
        block_radius="16px",
        block_shadow="0 8px 32px 0 rgba(99, 102, 241, 0.04)",
        
        # Text controls
        body_text_color="#1e293b",
        body_text_color_subdued="#475569",
        
        # Inputs & Selects
        input_background_fill="rgba(255, 255, 255, 0.9)",
        input_border_color="rgba(15, 23, 42, 0.12)",
        input_border_color_focus="#6366f1",
        input_radius="12px",
        
        # Buttons
        button_primary_background_fill="linear-gradient(135deg, #4f46e5 0%, #9333ea 100%)",
        button_primary_background_fill_hover="linear-gradient(135deg, #4338ca 0%, #7e22ce 100%)",
        button_primary_border_color="transparent",
        button_primary_text_color="#ffffff",
        button_primary_text_color_hover="#ffffff",
        
        button_secondary_background_fill="rgba(255, 255, 255, 0.85)",
        button_secondary_border_color="rgba(15, 23, 42, 0.08)",
        button_secondary_text_color="#475569",
        button_secondary_text_color_hover="#1e293b",
        
        # Slider track & knob colors
        slider_color="#4f46e5",
    )

    with gr.Blocks(
        theme=theme,
        css=CUSTOM_CSS,
        title="unos Multilingual TTS & Voice Cloning",
    ) as demo:

        # ── Hero ──────────────────────────────────────────────────────────────
        gr.HTML("""
        <div class="hero-header">
          <div class="hero-title">🎤 unos Multilingual TTS & Voice Cloning</div>
          <p class="hero-sub">
            Natural speech synthesis powered by <strong>Meta's MMS-TTS</strong> and Zero-shot Voice Cloning powered by <strong>Coqui's XTTS-v2</strong><br>
            100% free · fully open-source · runs offline · no authentication required
          </p>
          <div class="lang-pills">
            <span class="lang-pill">🇬🇧 English</span>
            <span class="lang-pill">🇮🇳 Hindi</span>
            <span class="lang-pill">🇮🇳 Bengali</span>
            <span class="lang-pill">🇮🇳 Gujarati</span>
            <span class="lang-pill">🇮🇳 Kannada</span>
            <span class="lang-pill">🇮🇳 Malayalam</span>
            <span class="lang-pill">🇮🇳 Marathi</span>
            <span class="lang-pill">🇮🇳 Odia</span>
            <span class="lang-pill">🇮🇳 Punjabi</span>
            <span class="lang-pill">🇮🇳 Tamil</span>
            <span class="lang-pill">🇮🇳 Telugu</span>
            <span class="lang-pill">🇮🇳 Assamese</span>
            <span class="lang-pill">🇮🇳 Dogri</span>
            <span class="lang-pill">🇮🇳 Urdu</span>
          </div>
        </div>
        """)

        with gr.Tabs():
            # ── TAB 1: Standard TTS ───────────────────────────────────────────
            with gr.Tab("🌐 Standard Text-to-Speech (MMS-TTS)"):
                with gr.Row(equal_height=False):
                    with gr.Column(scale=3, elem_classes=["panel-card"]):
                        gr.HTML('<div class="section-label">📝 Input Text</div>')
                        text_input = gr.Textbox(
                            label="Text to Synthesise",
                            placeholder="Type or paste text here in any of the 14 supported languages …",
                            lines=6,
                            max_lines=16,
                            show_label=False,
                            elem_id="text-input",
                        )
                        with gr.Row():
                            lang_dropdown = gr.Dropdown(
                                choices=LANGUAGES,
                                value="English",
                                label="🌐 Language",
                                scale=2,
                            )
                            sample_btn = gr.Button(
                                "📋 Load Sample Text",
                                variant="secondary",
                                scale=1,
                                size="sm",
                            )
                        gr.Markdown(
                            "ℹ️ **Model Info**: This tab uses Meta's MMS-TTS. "
                            "Emotion / tone and voice style/gender controls are not available "
                            "because each language uses a single fixed, pre-trained speaker checkpoint. "
                            "Speed can be adjusted using the speed tuning slider on the right."
                        )

                    with gr.Column(scale=2, elem_classes=["panel-card"]):
                        gr.HTML('<div class="section-label">⚙️ Fine-tuning</div>')
                        speed_slider = gr.Slider(
                            minimum=0.25,
                            maximum=2.0,
                            value=1.0,
                            step=0.05,
                            label="🐢 Speed  ← slow · · · fast →",
                            info="1.0 = natural pace",
                        )
                        generate_btn = gr.Button(
                            "🎤 Generate Speech",
                            variant="primary",
                            elem_id="gen-btn",
                        )
                        gr.HTML('<div class="section-label" style="margin-top:20px;">🔈 Output</div>')
                        audio_output = gr.Audio(
                            label="Generated Audio",
                            type="filepath",
                            elem_id="audio-out",
                            show_download_button=True,
                        )
                        status_box = gr.Textbox(
                            label="Status",
                            interactive=False,
                            lines=2,
                            elem_id="status-box",
                            placeholder="Status will appear here after generation …",
                        )
                        with gr.Row():
                            wav_download = gr.File(
                                label="⬇️ WAV Download",
                                visible=True,
                                file_count="single",
                            )
                
                # Examples
                gr.HTML('<hr style="border-color:rgba(15,23,42,0.08);margin:20px 0">')
                gr.HTML('<div class="section-label" style="text-align:center">💡 Quick Examples – click a row to populate the form</div>')
                gr.Examples(
                    examples=[
                        ["Hello! This is a demonstration of natural English speech synthesis.", "English", 1.0],
                        ["आज का मौसम बहुत सुहाना है। धूप खिली हुई है और हवा ताज़ी है।", "Hindi", 1.0],
                        ["আমাদের বাংলা ভাষা অত্যন্ত মিষ্টি এবং সমৃদ্ধ।", "Bengali", 1.0],
                        ["ಕನ್ನಡ ನಾಡಿನ ಸಂಸ್ಕೃತಿ ಮತ್ತು ಸಾಹಿತ್ಯ ಅತ್ಯಂತ ಶ್ರೀಮಂತವಾಗಿದೆ.", "Kannada", 1.0],
                        ["தமிழ் மொழி உலகின் மிகப் பழமையான மொழிகளில் ஒன்று.", "Tamil", 1.0],
                        ["తెలుగు భాష అత్యంత తీయని భాషలలో ఒకటి. దీని సాహిత్యం చాలా గొప్పది.", "Telugu", 1.0],
                    ],
                    inputs=[text_input, lang_dropdown, speed_slider],
                    label=None,
                )

            # ── TAB 2: Voice Cloning ──────────────────────────────────────────
            with gr.Tab("👥 Zero-shot Voice Cloning (XTTS-v2)"):
                with gr.Row(equal_height=False):
                    with gr.Column(scale=3, elem_classes=["panel-card"]):
                        gr.HTML('<div class="section-label">📝 Text to Speak</div>')
                        clone_text_input = gr.Textbox(
                            label="Text to Speak in Cloned Voice",
                            placeholder="Enter text to speak here...",
                            lines=4,
                            show_label=False,
                        )
                        
                        gr.HTML('<div class="section-label">🎙️ Reference Speaker Clip (3-5s)</div>')
                        clone_ref_audio = gr.Audio(
                            label="Record or upload reference clip",
                            type="filepath",
                            sources=["microphone", "upload"],
                        )
                        
                        clone_lang_dropdown = gr.Dropdown(
                            choices=["English", "Hindi"],
                            value="English",
                            label="🌐 Language",
                        )
                        
                        gr.Markdown(
                            "⚠️ **Kannada & Telugu Cloning Info**: Voice cloning is only available for **English** and **Hindi** via XTTS-v2. "
                            "Kannada and Telugu voice cloning is **not available** due to the lack of an ungated open-source model. "
                            "(AI4Bharat's IndicF5 model was evaluated but rejected as it requires Hugging Face login authentication / manual gated approval)."
                        )

                    with gr.Column(scale=2, elem_classes=["panel-card"]):
                        gr.HTML('<div class="section-label">⚙️ Fine-tuning</div>')
                        clone_speed_slider = gr.Slider(
                            minimum=0.25,
                            maximum=2.0,
                            value=1.0,
                            step=0.05,
                            label="🐢 Speed  ← slow · · · fast →",
                            info="1.0 = natural pace",
                        )
                        clone_generate_btn = gr.Button(
                            "👤 Generate Cloned Speech",
                            variant="primary",
                            elem_id="gen-btn",
                        )
                        gr.HTML('<div class="section-label" style="margin-top:20px;">🔈 Output</div>')
                        clone_audio_output = gr.Audio(
                            label="Cloned Audio Output",
                            type="filepath",
                            show_download_button=True,
                        )
                        clone_status_box = gr.Textbox(
                            label="Status",
                            interactive=False,
                            lines=2,
                            placeholder="Status will appear here after cloning …",
                        )
                        with gr.Row():
                            clone_wav_download = gr.File(
                                label="⬇️ WAV Download",
                                visible=True,
                                file_count="single",
                            )
                
                # Examples
                gr.HTML('<hr style="border-color:rgba(15,23,42,0.08);margin:20px 0">')
                gr.HTML('<div class="section-label" style="text-align:center">💡 Quick Cloning Examples</div>')
                gr.Examples(
                    examples=[
                        ["Hello, this is a cloned voice test in English. The model synthesizes my voice using a brief recording.", "English", 1.0],
                        ["नमस्ते, यह एक आवाज क्लोन परीक्षण है।  मेरी रिकॉर्डिंग के आधार पर मेरी आवाज में बात करेगा।", "Hindi", 1.0],
                    ],
                    inputs=[clone_text_input, clone_lang_dropdown, clone_speed_slider],
                    label=None,
                )

        # ── Info accordion ────────────────────────────────────────────────────
        with gr.Accordion("ℹ️ About this application", open=False):
            gr.Markdown("""
### Multilingual TTS & Zero-shot Voice Cloning

This application contains two modules:
1. **Standard Text-to-Speech (MMS-TTS)**: Uses Meta's Massively Multilingual Speech (MMS) checkpoints built on the VITS architecture. 
   - Supports 14 languages natively.
   - Entirely open and non-gated, weights are cached locally.
2. **Zero-shot Voice Cloning (XTTS-v2)**: Uses Coqui's XTTS-v2 model to synthesize new speech using a 3-5 second clip of a speaker's voice.
   - Supports English and Hindi.
   - Bypasses gated access requirements using open-license non-commercial weights.
   - **Kannada/Telugu Voice Cloning**: Evaluated AI4Bharat's IndicF5, but rejected because it is gated and requires manual repository approval on Hugging Face. No viable ungated alternative for Kannada/Telugu voice cloning was found.
            """)

        # ── Footer ────────────────────────────────────────────────────────────
        gr.HTML("""
        <div style="text-align:center;padding:16px 0 4px;color:#475569;font-size:0.78rem">
          Built with ❤️ using
          <a href="https://huggingface.co/facebook/mms-tts" target="_blank"
             style="color:#4f46e5;font-weight:600">Meta MMS-TTS</a> ·
          <a href="https://huggingface.co/coqui/XTTS-v2" target="_blank"
             style="color:#4f46e5;font-weight:600">Coqui XTTS-v2</a> ·
          <a href="https://www.gradio.app" target="_blank"
             style="color:#4f46e5;font-weight:600">Gradio</a> ·
          <a href="https://pytorch.org" target="_blank"
             style="color:#4f46e5;font-weight:600">PyTorch</a>
        </div>
        """)

        # ── Wiring ────────────────────────────────────────────────────────────
        sample_btn.click(
            fn=load_sample_text,
            inputs=[lang_dropdown],
            outputs=[text_input],
        )

        generate_btn.click(
            fn=generate_speech,
            inputs=[
                text_input,
                lang_dropdown,
                speed_slider,
            ],
            outputs=[audio_output, wav_download, status_box],
        )

        clone_generate_btn.click(
            fn=clone_voice_speech,
            inputs=[
                clone_text_input,
                clone_lang_dropdown,
                clone_ref_audio,
                clone_speed_slider,
            ],
            outputs=[clone_audio_output, clone_wav_download, clone_status_box],
        )

    return demo


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",   # accessible on local network
        server_port=7860,
        share=False,             # set True to get a public Gradio link
        inbrowser=True,          # auto-open browser
        show_error=True,
    )

