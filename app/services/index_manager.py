"""Index manager service for detecting, validating, and auto-building FAISS databases."""

import hashlib
import json
import os
import time
from typing import Any, Dict
from app.services.indexing_service import IndexingService
from config.settings import settings
from core.logger import logger


class IndexManager:
    """Manages index files state, hash tracking, and automated rebuild hooks."""

    @staticmethod
    def get_knowledge_hash() -> str:
        """Computes MD5 hash representing paths and modification times of files.

        Returns:
            str: Hash digest string.
        """
        doc_dir = settings.DOCUMENTS_DIR
        if not os.path.exists(doc_dir):
            return ""

        hash_md5 = hashlib.md5()
        for root, _, files in os.walk(doc_dir):
            for file in sorted(files):
                path = os.path.join(root, file)
                try:
                    stat = os.stat(path)
                    hash_md5.update(path.encode("utf-8"))
                    hash_md5.update(str(stat.st_mtime).encode("utf-8"))
                except OSError:
                    pass
        return hash_md5.hexdigest()

    @classmethod
    def index_needs_rebuild(cls) -> bool:
        """Determines if the database needs to be rebuilt.

        Checks if FAISS files are missing or modified.

        Returns:
            bool: True if rebuild is required.
        """
        store_path = settings.VECTOR_DB_PATH
        faiss_file = os.path.join(store_path, "index.faiss")
        pkl_file = os.path.join(store_path, "index.pkl")
        meta_file = os.path.join(store_path, "index_metadata.json")

        # Rebuild if files do not exist
        if not os.path.exists(faiss_file) or not os.path.exists(pkl_file):
            return True

        if not os.path.exists(meta_file):
            return True

        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            saved_hash = meta.get("knowledge_hash", "")
            current_hash = cls.get_knowledge_hash()
            return saved_hash != current_hash
        except Exception:
            return True

    @classmethod
    def ensure_index_ready(cls) -> None:
        """Verifies FAISS files on startup and runs auto-rebuild if outdated."""
        if cls.index_needs_rebuild():
            logger.info("IndexManager: FAISS index missing or outdated. Triggering auto-rebuild...")
            cls.rebuild_index()
        else:
            logger.info("IndexManager: FAISS index is up-to-date. Ready.")

    @classmethod
    def rebuild_index(cls) -> Any:
        """Executes indexing, records metrics, and saves state metadata.

        Returns:
            IndexResponse: Indexing statistics outcome.
        """
        start_time = time.time()
        service = IndexingService()
        res = service.build_index()
        duration = time.time() - start_time

        if res.status == "success":
            current_hash = cls.get_knowledge_hash()
            meta = {
                "knowledge_hash": current_hash,
                "indexing_time_s": duration,
                "documents_processed": res.documents_processed,
                "chunks_created": res.chunks_created,
                "timestamp": time.time(),
            }

            os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
            meta_file = os.path.join(settings.VECTOR_DB_PATH, "index_metadata.json")
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=4)

            logger.info(f"IndexManager: FAISS index rebuilt successfully in {duration:.2f}s.")
        else:
            logger.error(f"IndexManager: Index rebuild failed: {res.message}")

        return res

    @classmethod
    def delete_index(cls) -> None:
        """Purges local FAISS file stores from host paths."""
        store_path = settings.VECTOR_DB_PATH
        faiss_file = os.path.join(store_path, "index.faiss")
        pkl_file = os.path.join(store_path, "index.pkl")
        meta_file = os.path.join(store_path, "index_metadata.json")

        for f in [faiss_file, pkl_file, meta_file]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                    logger.info(f"IndexManager: Deleted index file: '{f}'")
                except OSError as e:
                    logger.error(f"IndexManager: Failed to delete '{f}': {e}")
