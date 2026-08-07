"""Helper script to clear memory-cached query answers and statistics."""

import os
import sys

# Add workspace directory to python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cache.cache_manager import CacheManager
from core.logger import logger


def main() -> None:
    """Invokes CacheManager clear commands."""
    logger.info("CLI: Clearing in-memory resolved answer caches...")
    cache = CacheManager()
    cache.clear()
    logger.info("CLI: Answer caching layers purged successfully.")


if __name__ == "__main__":
    main()
