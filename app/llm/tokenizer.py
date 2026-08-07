"""TokenizerLoader class implementing singleton pattern for local tokenizations."""

from typing import Any

from transformers import AutoTokenizer

from config.settings import settings
from core.logger import logger


class TokenizerLoader:
    """Singleton tokenizer loader that caches model tokenizers."""

    _instance = None

    def __new__(cls) -> "TokenizerLoader":
        if cls._instance is None:
            cls._instance = super(TokenizerLoader, cls).__new__(cls)
            cls._instance._tokenizer = None
        return cls._instance

    def load_tokenizer(self) -> Any:
        """Loads and returns the HuggingFace model tokenizer."""
        if self._tokenizer is not None:
            return self._tokenizer

        model_name = settings.LLM_MODEL_NAME
        logger.info(f"Loading tokenizer interface for: '{model_name}'...")

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
        except Exception as e:
            logger.exception(f"Failed to load tokenizer for model '{model_name}': {e}")
            raise e

        return self._tokenizer
