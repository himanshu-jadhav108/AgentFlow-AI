"""Model manager service for checking and downloading HuggingFace models."""

import os
from config.settings import settings
from core.logger import logger


class ModelManager:
    """Manages downloading, verifying caching, and local loading of LLM weights."""

    @staticmethod
    def download_model(model_name: str = None) -> None:
        """Pre-downloads and caches model checkpoints from the HuggingFace Hub.

        Avoids repeated downloads using HuggingFace's internal caching.

        Args:
            model_name: Optional model identifier from HF. Defaults to config settings.
        """
        if not model_name:
            model_name = settings.LLM_MODEL_NAME

        # Skip model weight download if provider is Ollama
        if settings.LLM_PROVIDER == "ollama":
            logger.info("ModelManager: LLM provider is set to Ollama. Skipping Hub cache checks.")
            return

        logger.info(f"ModelManager: Checking local cache for model '{model_name}'...")

        try:
            # We import here to avoid slow startup overheads when importing transformers
            from transformers import AutoModelForCausalLM, AutoTokenizer

            # 1. Download/load tokenizer
            logger.info("ModelManager: Syncing local tokenizer caches...")
            AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

            # 2. Download/load model weights
            logger.info("ModelManager: Syncing local model weights caches...")
            AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)

            logger.info(f"ModelManager: Local cache for '{model_name}' is verified and ready.")

        except Exception as e:
            logger.error(f"ModelManager: Failed to pre-download model '{model_name}': {e}")
            raise e
