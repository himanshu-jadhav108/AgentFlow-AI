"""Inference engine managing tokenization, execution, and string decoding."""

import time

import torch

from app.llm.model_loader import ModelLoader
from app.llm.tokenizer import TokenizerLoader
from core.logger import logger


class InferenceManager:
    """Manages model forwarding and execution timing stats."""

    def __init__(self) -> None:
        self.model_loader = ModelLoader()
        self.tokenizer_loader = TokenizerLoader()

    def generate_text(
        self, prompt: str, max_new_tokens: int = 350, temperature: float = 0.1
    ) -> str:
        """Executes text generation on the local cached model.

        Args:
            prompt: Text prompt compiled with instructions and context.
            max_new_tokens: Limit on newly decoded tokens.
            temperature: Sampling temperature (lower values enforce determinism).

        Returns:
            str: Grounded response string decoded from token lists.
        """
        start_time = time.time()

        # Load cached model and tokenizer instances
        model = self.model_loader.load_model()
        tokenizer = self.tokenizer_loader.load_tokenizer()
        device = self.model_loader.device

        logger.info(
            f"Starting local LLM inference (tokens={max_new_tokens}, temp={temperature})..."
        )

        try:
            # Convert string to input IDs on selected device
            inputs = tokenizer(prompt, return_tensors="pt").to(device)

            # Generate token sequence
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    do_sample=temperature > 0.0,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )

            # Slice output to isolate new tokens from input prompt
            input_length = inputs.input_ids.shape[1]
            generated_tokens = outputs[0][input_length:]

            # Decode tokens back into a readable string
            decoded_text = tokenizer.decode(
                generated_tokens, skip_special_tokens=True
            ).strip()

            latency_s = time.time() - start_time
            logger.info(f"Local LLM inference completed in {latency_s:.2f}s.")
            return decoded_text

        except Exception as e:
            logger.exception(f"Error executing local LLM inference: {e}")
            raise e
