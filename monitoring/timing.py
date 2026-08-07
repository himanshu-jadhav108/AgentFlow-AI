"""Timing utility capturing execution latency block durations."""

import time
from contextlib import contextmanager
from typing import Callable, Generator, Optional
from core.logger import logger


@contextmanager
def time_block(
    name: str,
    callback: Optional[Callable[[float], None]] = None,
) -> Generator[None, None, None]:
    """Context manager to measure code block execution speed.

    Args:
        name: Name of the code block.
        callback: Function to invoke with duration in milliseconds.
    """
    start = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start) * 1000
        logger.debug(f"Timing block '{name}' finished in {duration_ms:.2f}ms")
        if callback:
            try:
                callback(duration_ms)
            except Exception as e:
                logger.warning(f"Failed to record metric callback for '{name}': {e}")
