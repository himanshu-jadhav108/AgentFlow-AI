"""ModelLoader class implementing singleton pattern for local LLM execution."""

import os
import time
from typing import Any
import psutil
import torch
from transformers import AutoModelForCausalLM
from config.settings import settings
from core.logger import logger


class ModelLoader:
    """Singleton model loader that loads the local LLM model once."""

    _instance = None

    def __new__(cls) -> "ModelLoader":
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._model = None
            cls._instance._device = None
            cls._instance._load_time = 0.0
        return cls._instance

    def load_model(self) -> Any:
        """Loads and returns the HuggingFace model cache.

        Detects CUDA or CPU device environments.
        """
        if self._model is not None:
            return self._model

        start_time = time.time()
        model_name = settings.LLM_MODEL_NAME

        # 1. Device Detection
        if torch.cuda.is_available():
            self._device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"GPU Device detected: {gpu_name}. Selecting CUDA device.")
        else:
            self._device = "cpu"
            logger.info("No GPU detected. Selecting CPU device execution.")

        logger.info(f"Loading local LLM model: '{model_name}' on device '{self._device}'...")

        # 2. Memory usage monitoring
        process = psutil.Process(os.getpid())
        initial_mem_mb = process.memory_info().rss / (1024 * 1024)

        try:
            # Select precision (float16 for GPU, float32 for CPU)
            torch_dtype = torch.float16 if self._device == "cuda" else torch.float32

            # Load weights
            self._model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch_dtype,
                device_map=self._device,
            )

            self._load_time = time.time() - start_time
            from monitoring.metrics import metrics
            metrics.record_model_load(self._load_time * 1000)
            final_mem_mb = process.memory_info().rss / (1024 * 1024)
            ram_delta = final_mem_mb - initial_mem_mb

            logger.info(
                f"LLM loaded successfully in {self._load_time:.2f}s. "
                f"Device: {self._device}. "
                f"RAM usage delta: {ram_delta:.2f} MB. "
                f"GPU allocated: {torch.cuda.memory_allocated() / (1024*1024) if self._device == 'cuda' else 0.0:.2f} MB."
            )
        except Exception as e:
            logger.exception(f"Failed to load LLM model '{model_name}': {e}")
            raise e

        return self._model

    @property
    def device(self) -> str:
        """Returns the device selected for execution."""
        if self._device is None:
            self.load_model()
        return self._device

    @property
    def load_time(self) -> float:
        """Returns model load duration in seconds."""
        return self._load_time
