"""Helper script to pre-download model weights and tokenizers from HuggingFace."""

import os
import sys

# Add workspace directory to python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.model_manager import ModelManager
from core.logger import logger


def main() -> None:
    """Invokes ModelManager model caching download flows."""
    logger.info("CLI: Initiating manual HuggingFace model caching sync...")
    try:
        ModelManager.download_model()
        logger.info("CLI: Model pre-download sync complete.")
    except Exception as e:
        logger.error(f"CLI: Model download failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
