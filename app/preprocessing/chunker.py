"""Document chunking service that splits documents into smaller segments."""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.schemas.document import Document
from core.logger import logger


class DocumentChunker:
    """Service to divide long text documents into overlapping semantic chunks."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        """Initialize the chunker with configured segment size and overlap."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

    def chunk_document(self, doc: Document) -> List[Document]:
        """Splits a single Document into a list of smaller chunked Documents.

        Args:
            doc: The source Document object.

        Returns:
            List[Document]: List of chunked Document instances with enhanced metadata.
        """
        if not doc.content.strip():
            logger.warning(f"Attempted to chunk document with empty content: {doc.id}")
            return []

        splits = self.splitter.split_text(doc.content)
        chunks: List[Document] = []

        for idx, text in enumerate(splits):
            chunk_id = f"{doc.id}_c{idx}"

            # Simple token estimation: word count / 0.75
            word_count = len(text.split())
            token_estimate = int(word_count / 0.75) if word_count > 0 else 0

            # Inherit parent metadata and add chunk-specific tracking tags
            chunk_metadata = {
                **doc.metadata,
                "chunk_id": chunk_id,
                "chunk_index": idx,
                "token_estimate": token_estimate,
                "parent_id": doc.id,
            }

            chunks.append(
                Document(
                    id=chunk_id,
                    content=text.strip(),
                    metadata=chunk_metadata,
                )
            )

        logger.debug(
            f"Split document {doc.id} ({doc.metadata.get('filename', 'unknown')}) into {len(chunks)} chunks."
        )
        return chunks

    def chunk_documents(self, docs: List[Document]) -> List[Document]:
        """Splits a batch of documents.

        Args:
            docs: List of source Documents.

        Returns:
            List[Document]: Flattened list of all generated chunks.
        """
        all_chunks: List[Document] = []
        for doc in docs:
            all_chunks.extend(self.chunk_document(doc))
        logger.info(
            f"Chunked {len(docs)} documents into {len(all_chunks)} total chunks."
        )
        return all_chunks
