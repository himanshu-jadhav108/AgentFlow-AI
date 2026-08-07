"""Helper script to rebuild the FAISS vector index database."""

import os
import sys

# Add workspace directory to python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.index_manager import IndexManager
from core.logger import logger


def main() -> None:
    """Executes FAISS index regeneration."""
    logger.info("CLI: Initiating manual FAISS index rebuild...")
    res = IndexManager.rebuild_index()
    if res.status == "success":
        logger.info(
            f"CLI: Index rebuilt successfully. "
            f"Processed: {res.documents_processed} documents. "
            f"Created: {res.chunks_created} chunks."
        )
    else:
        logger.error(f"CLI: Rebuild failed: {res.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
