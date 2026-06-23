"""
download_models.py
──────────────────
Downloads and caches the standard MMS-TTS and Coqui XTTS-v2 model weights
from Hugging Face so that the web application can run completely offline.
"""

import os
import argparse
import logging
from src.presets import LANG_MODELS

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("downloader")

def main():
    parser = argparse.ArgumentParser(description="Download model weights for offline Multilingual TTS & Voice Cloning.")
    parser.add_argument(
        "--all-mms",
        action="store_true",
        help="Download MMS-TTS models for all 14 supported languages (default is English & Hindi only)."
    )
    parser.add_argument(
        "--no-xtts",
        action="store_true",
        help="Skip downloading the Coqui XTTS-v2 voice cloning model (~1.8 GB)."
    )
    args = parser.parse_args()

    logger.info("=========================================================")
    logger.info("  UNOS Multilingual TTS & Voice Cloning weight downloader")
    logger.info("=========================================================")

    # 1. Download MMS-TTS Models
    selected_langs = list(LANG_MODELS.keys()) if args.all_mms else ["English", "Hindi"]
    logger.info("📥 [1/2] Downloading MMS-TTS models for: %s", ", ".join(selected_langs))
    
    from transformers import VitsModel, AutoTokenizer
    for lang in selected_langs:
        model_id = LANG_MODELS[lang]
        logger.info("⏳ Downloading tokenizer & model for %s ('%s')...", lang, model_id)
        try:
            AutoTokenizer.from_pretrained(model_id)
            VitsModel.from_pretrained(model_id)
            logger.info("✅ Finished downloading %s model.", lang)
        except Exception as exc:
            logger.error("❌ Failed downloading model for %s: %s", lang, exc)

    # 2. Download XTTS-v2
    if not args.no_xtts:
        logger.info("📥 [2/2] Downloading Coqui XTTS-v2 model (~1.8 GB)...")
        os.environ['COQUI_TOS_AGREED'] = '1'
        try:
            from TTS.api import TTS
            logger.info("⏳ Initiating XTTS-v2 download and setup...")
            TTS('tts_models/multilingual/multi-dataset/xtts_v2')
            logger.info("✅ Finished downloading Coqui XTTS-v2 model.")
        except Exception as exc:
            logger.error("❌ Failed downloading Coqui XTTS-v2: %s", exc)
    else:
        logger.info("⏭️ [2/2] Skipping Coqui XTTS-v2 model download.")

    logger.info("=========================================================")
    logger.info("  Download checks finished. The models are cached locally!")
    logger.info("=========================================================")

if __name__ == "__main__":
    main()
