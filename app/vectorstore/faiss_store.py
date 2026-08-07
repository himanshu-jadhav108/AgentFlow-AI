"""FAISS Vector Store manager for indexing and searching document embeddings."""

import os
import shutil
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument

from app.embeddings.embedding_model import LocalEmbeddingManager
from app.schemas.document import Document
from core.logger import logger


class FAISSStoreManager:
    """Manager for FAISS vector operations, index persistence, and duplicate prevention."""

    def __init__(self) -> None:
        """Initialize the manager with local embedding model."""
        self.embeddings = LocalEmbeddingManager().get_embeddings()
        self.db: Optional[FAISS] = None

    def create_index(self, documents: List[Document]) -> None:
        """Create a new FAISS index from a list of documents.

        Args:
            documents: List of domain Document models to index.
        """
        if not documents:
            logger.warning("Attempted to create FAISS index with zero documents.")
            return

        logger.info(f"Creating FAISS index with {len(documents)} document chunks...")
        lc_docs = [
            LCDocument(
                page_content=doc.content,
                metadata={
                    **doc.metadata,
                    "chunk_id": doc.id,
                    "document_id": doc.metadata.get("document_id", doc.id),
                },
            )
            for doc in documents
        ]
        ids = [doc.id for doc in documents]

        self.db = FAISS.from_documents(
            lc_docs, self.embeddings, ids=ids, distance_strategy="COSINE"
        )
        logger.info("FAISS index created successfully in-memory.")

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the index, deleting existing documents with matching IDs.

        This guarantees that duplicate vectors are never created for the same chunk.

        Args:
            documents: List of domain Documents to insert or update.
        """
        if not documents:
            return

        if self.db is None:
            logger.info(
                "No index currently loaded. Creating new index instead of appending."
            )
            self.create_index(documents)
            return

        logger.info(f"Adding/Updating {len(documents)} chunks in FAISS index...")
        lc_docs = [
            LCDocument(
                page_content=doc.content,
                metadata={
                    **doc.metadata,
                    "chunk_id": doc.id,
                    "document_id": doc.metadata.get("document_id", doc.id),
                },
            )
            for doc in documents
        ]
        ids = [doc.id for doc in documents]

        # Extract existing IDs to avoid duplicates
        existing_ids = set(self.db.index_to_docstore_id.values())
        duplicate_ids = [doc_id for doc_id in ids if doc_id in existing_ids]

        if duplicate_ids:
            logger.debug(
                f"Removing {len(duplicate_ids)} existing duplicate chunks before inserting."
            )
            self.db.delete(duplicate_ids)

        self.db.add_documents(lc_docs, ids=ids)
        logger.info("FAISS index updated.")

    def save_index(self, folder_path: str) -> None:
        """Save the FAISS index to the local filesystem.

        Args:
            folder_path: Target directory to save FAISS binaries.
        """
        if self.db is None:
            logger.error("Cannot save index: FAISS db is not initialized.")
            return

        logger.info(f"Saving FAISS index to disk: {folder_path}")
        os.makedirs(folder_path, exist_ok=True)
        self.db.save_local(folder_path)
        logger.info("FAISS index saved successfully.")

    def load_index(self, folder_path: str) -> bool:
        """Load the FAISS index from the local filesystem.

        Args:
            folder_path: Directory containing the FAISS index files.

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        if not os.path.exists(os.path.join(folder_path, "index.faiss")):
            logger.warning(f"No FAISS index found at path: {folder_path}")
            return False

        logger.info(f"Loading FAISS index from disk: {folder_path}")
        try:
            self.db = FAISS.load_local(
                folder_path, self.embeddings, allow_dangerous_deserialization=True
            )
            logger.info("FAISS index loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index from {folder_path}: {e}")
            return False

    def delete_index(self, folder_path: str) -> None:
        """Clears local FAISS database and deletes persisted files on disk.

        Args:
            folder_path: Target directory of the index files.
        """
        logger.info(f"Deleting FAISS index directory and state: {folder_path}")
        self.db = None
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                logger.info(f"Deleted directory: {folder_path}")
            except Exception as e:
                logger.error(f"Failed to delete directory {folder_path}: {e}")

    def rebuild_index(self, documents: List[Document], folder_path: str) -> None:
        """Clears the existing index, builds a new one from scratch, and persists it.

        Args:
            documents: Complete document set to index.
            folder_path: Target directory.
        """
        logger.info(f"Rebuilding index at {folder_path}...")
        self.delete_index(folder_path)
        self.create_index(documents)
        self.save_index(folder_path)
