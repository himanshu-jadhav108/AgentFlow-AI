"""Indexing service to orchestrate the ingestion and indexing pipeline."""

import os
import time
from typing import Optional

from app.loaders.json_loader import JSONCaseLoader
from app.loaders.markdown_loader import MarkdownLoader
from app.preprocessing.chunker import DocumentChunker
from app.preprocessing.cleaner import TextCleaner
from app.schemas.retrieval import IndexResponse
from app.vectorstore.faiss_store import FAISSStoreManager
from config.settings import settings
from core.logger import logger


class IndexingService:
    """Orchestration service that loads, cleans, chunks, and indexes all knowledge base sources."""

    def __init__(self, store_manager: Optional[FAISSStoreManager] = None) -> None:
        """Initialize the indexing service with cleaner, chunker, and store manager."""
        self.store_manager = store_manager or FAISSStoreManager()
        self.cleaner = TextCleaner()
        # Chunker settings from configuration (size 1000, overlap 200)
        self.chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)

    def build_index(self) -> IndexResponse:
        """Runs the full indexing pipeline: Loader -> Cleaner -> Chunker -> FAISS.

        Returns:
            IndexResponse: Summary of the indexing operation results.
        """
        start_time = time.time()
        logger.info("Starting complete vector index rebuild pipeline...")

        # 1. Setup paths
        docs_dir = settings.DOCUMENTS_DIR
        kb_dir = os.path.join(docs_dir, "knowledge_base")
        cases_file = os.path.join(docs_dir, "resolved_cases.json")

        # Ensure documents directory structure exists
        os.makedirs(kb_dir, exist_ok=True)

        # 2. Load documents
        loaded_docs = []

        # Load Markdown knowledge base files
        md_loader = MarkdownLoader(kb_dir)
        md_docs = md_loader.load()
        loaded_docs.extend(md_docs)

        # Load JSON resolved cases
        if os.path.exists(cases_file):
            json_loader = JSONCaseLoader(cases_file)
            case_docs = json_loader.load()
            loaded_docs.extend(case_docs)
        else:
            logger.warning(
                f"Resolved cases JSON file not found at: {cases_file}. Skipping JSON loading."
            )

        if not loaded_docs:
            msg = "No documents or cases found to index. Index was not updated."
            logger.warning(msg)
            return IndexResponse(
                status="warning",
                documents_processed=0,
                chunks_created=0,
                message=msg,
            )

        # 3. Clean document text
        logger.info(f"Cleaning text content of {len(loaded_docs)} documents...")
        cleaned_docs = []
        for doc in loaded_docs:
            cleaned_content = self.cleaner.clean(doc.content)
            # Create a new document with cleaned content
            cleaned_docs.append(
                doc.__class__(
                    id=doc.id,
                    content=cleaned_content,
                    metadata=doc.metadata,
                )
            )

        # 4. Chunk documents
        logger.info("Chunking cleaned documents...")
        chunks = self.chunker.chunk_documents(cleaned_docs)
        if not chunks:
            msg = "No document chunks were created during chunking."
            logger.error(msg)
            return IndexResponse(
                status="error",
                documents_processed=len(loaded_docs),
                chunks_created=0,
                message=msg,
            )

        # 5. Build and persist FAISS index
        db_path = settings.VECTOR_DB_PATH
        logger.info(
            f"Indexing {len(chunks)} chunks in FAISS and persisting to {db_path}..."
        )
        try:
            self.store_manager.rebuild_index(chunks, db_path)
        except Exception as e:
            error_msg = f"Failed to build or save FAISS index: {e}"
            logger.error(error_msg)
            return IndexResponse(
                status="error",
                documents_processed=len(loaded_docs),
                chunks_created=len(chunks),
                message=error_msg,
            )

        elapsed = time.time() - start_time
        msg = f"Successfully rebuilt FAISS vector index with {len(chunks)} chunks in {elapsed:.2f}s."
        logger.info(msg)

        return IndexResponse(
            status="success",
            documents_processed=len(loaded_docs),
            chunks_created=len(chunks),
            message=msg,
        )
