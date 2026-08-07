"""Setup installer validating environment resources and syncing caches."""

import os
import sys

# Add workspace directory to python search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import shutil
import subprocess

from core.logger import logger


def check_dependencies() -> bool:
    """Verifies system specifications and basic python compatibility libraries."""
    logger.info("Setup: Running dependency and resource checks...")

    # 1. Python version check
    py_ver = sys.version_info
    if py_ver.major < 3 or (py_ver.major == 3 and py_ver.minor < 11):
        logger.error(
            f"Setup Error: Python 3.11+ is required. Found version: {sys.version}"
        )
        return False
    logger.info(f"Setup: Python Version OK ({sys.version.split()[0]})")

    # 2. Disk Space check (Need at least 2GB free space)
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024**3)
    if free_gb < 2.0:
        logger.warning(
            f"Setup Warning: Low free disk space ({free_gb:.2f} GB). HuggingFace models may fail to download."
        )
    else:
        logger.info(f"Setup: Free disk space OK ({free_gb:.2f} GB)")

    # 3. Torch and CUDA check
    try:
        import torch

        cuda_available = torch.cuda.is_available()
        logger.info(f"Setup: PyTorch detected. CUDA available: {cuda_available}")
        if cuda_available:
            logger.info(f"Setup: GPU detected: {torch.cuda.get_device_name(0)}")
    except ImportError:
        logger.warning(
            "Setup Warning: PyTorch is not installed in the active path yet."
        )

    return True


def install_dependencies() -> None:
    """Runs pip install requirement constraints."""
    logger.info("Setup: Installing python dependency requirements...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        logger.info("Setup: Dependency installation completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Setup Error: Failed to install requirements: {e}")
        raise e


def sync_resources() -> None:
    """Pre-downloads HF weight models and builds FAISS index databases."""
    logger.info("Setup: Initializing AI resource managers...")

    # Load Settings
    from app.services.index_manager import IndexManager
    from app.services.model_manager import ModelManager
    from config.settings import settings

    logger.info(
        f"Setup: Checking model configuration settings ({settings.LLM_MODEL_NAME})..."
    )
    ModelManager.download_model()

    logger.info("Setup: Initializing FAISS indexing pipeline...")
    IndexManager.rebuild_index()


def run_test_suite() -> None:
    """Runs pytest to verify code validity."""
    logger.info("Setup: Executing automated test suite validations...")
    try:
        subprocess.run([sys.executable, "-m", "pytest"], check=True)
        logger.info("Setup: All unit and integration test assertions passed!")
    except subprocess.CalledProcessError:
        logger.warning("Setup Alert: Some tests failed. Please review tests logs.")


def main() -> None:
    """Orchestrates system installation and verification."""
    logger.info("=== STARTING AGENTFLOW AI INSTALLATION UTILITY ===")
    if not check_dependencies():
        sys.exit(1)

    try:
        install_dependencies()
        sync_resources()
        run_test_suite()
        logger.info("=== AGENTFLOW AI SETUP COMPLETED SUCCESSFULLY! ===")
    except Exception as e:
        logger.error(f"Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
