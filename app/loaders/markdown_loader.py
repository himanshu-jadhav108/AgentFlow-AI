"""Markdown document loader for the knowledge base."""

import hashlib
import os
from typing import List

from app.schemas.document import Document
from core.logger import logger


class MarkdownLoader:
    """Loader to parse and extract structured Document entities from Markdown files."""

    def __init__(self, directory_path: str) -> None:
        """Initialize the loader with target directory path."""
        self.directory_path = directory_path

    def load(self) -> List[Document]:
        """Loads and parses all markdown files in the target directory.

        Returns:
            List[Document]: List of parsed Document objects.
        """
        documents: List[Document] = []

        if not os.path.exists(self.directory_path):
            logger.error(f"Markdown directory does not exist: {self.directory_path}")
            return documents

        if not os.path.isdir(self.directory_path):
            logger.error(f"Path is not a directory: {self.directory_path}")
            return documents

        logger.info(f"Scanning directory for Markdown files: {self.directory_path}")
        for root, _, files in os.walk(self.directory_path):
            for file in files:
                if not file.endswith((".md", ".markdown")):
                    continue

                file_path = os.path.join(root, file)
                try:
                    doc = self._parse_file(file_path, file)
                    if doc:
                        documents.append(doc)
                except Exception as e:
                    logger.error(f"Unexpected error parsing file {file_path}: {e}")

        logger.info(f"Successfully loaded {len(documents)} markdown documents.")
        return documents

    def _parse_file(self, file_path: str, filename: str) -> Document | None:
        """Reads and extracts metadata from a single markdown file."""
        # Check if file is empty
        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.warning(f"Skipping empty markdown file: {file_path}")
                return None
        except OSError as e:
            logger.error(f"Cannot access file metadata for {file_path}: {e}")
            return None

        # Read file with encoding fallback
        content = ""
        encodings = ["utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                logger.warning(
                    f"Failed to read {file_path} with encoding {encoding}. Trying next."
                )
        else:
            logger.error(
                f"Failed to read {file_path} with any supported encoding ({encodings}). skipping."
            )
            return None

        if not content.strip():
            logger.warning(f"File contains only whitespace: {file_path}")
            return None

        # Extract Title: search for first '# Title' heading
        title = filename
        for line in content.splitlines():
            clean_line = line.strip()
            if clean_line.startswith("# "):
                title = clean_line[2:].strip()
                break

        # Generate a deterministic ID based on the relative path to avoid collision
        rel_path = os.path.relpath(file_path, self.directory_path)
        doc_id = hashlib.sha256(rel_path.encode("utf-8")).hexdigest()[:16]

        metadata = {
            "document_id": doc_id,
            "filename": filename,
            "source": file_path,
            "title": title,
            "file_size_bytes": file_size,
            "type": "knowledge_base",
        }

        logger.debug(
            f"Loaded markdown document: {filename} (ID: {doc_id}, Title: '{title}')"
        )
        return Document(id=doc_id, content=content, metadata=metadata)
