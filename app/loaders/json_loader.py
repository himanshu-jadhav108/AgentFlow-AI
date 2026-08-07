"""JSON loader for parsing resolved customer support cases."""

import json
import os
from typing import Any, Dict, List
from pydantic import BaseModel, Field, ValidationError
from app.schemas.document import Document
from core.logger import logger


class SupportCaseSchema(BaseModel):
    """Validation schema for incoming resolved support cases."""

    case_id: str = Field(..., alias="case_id")
    category: str
    question: str
    answer: str
    priority: int = Field(default=1, ge=1, le=5)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JSONCaseLoader:
    """Loader to parse, validate, and normalize resolved support cases from a JSON file."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with the resolved cases file path."""
        self.file_path = file_path

    def load(self) -> List[Document]:
        """Loads support cases from the JSON file and converts them to Documents.

        Returns:
            List[Document]: List of validated and formatted Case Documents.
        """
        documents: List[Document] = []

        if not os.path.exists(self.file_path):
            logger.error(f"Resolved cases file does not exist: {self.file_path}")
            return documents

        logger.info(f"Loading resolved cases from JSON file: {self.file_path}")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON syntax in file {self.file_path}: {e}")
            return documents
        except Exception as e:
            logger.error(f"Failed to read file {self.file_path}: {e}")
            return documents

        # Support both root lists and root dicts containing a list of cases
        cases_list: List[Any] = []
        if isinstance(raw_data, list):
            cases_list = raw_data
        elif isinstance(raw_data, dict):
            # Try to look for common list keys
            for key in ("cases", "data", "results"):
                if isinstance(raw_data.get(key), list):
                    cases_list = raw_data[key]
                    break
            else:
                logger.error("JSON dict root must contain a list of cases under 'cases', 'data', or 'results' keys.")
                return documents
        else:
            logger.error("JSON file root structure must be a list or object.")
            return documents

        for idx, item in enumerate(cases_list):
            try:
                # Use Pydantic to validate structure and set defaults
                # We support loading fields directly or with aliases if we have case_id
                case_data = SupportCaseSchema.model_validate(item)
                doc = self._normalize_case(case_data)
                documents.append(doc)
            except ValidationError as ve:
                logger.warning(f"Validation failed for case at index {idx} in {self.file_path}: {ve.json()}")
            except Exception as e:
                logger.error(f"Error parsing case at index {idx}: {e}")

        logger.info(f"Successfully loaded {len(documents)} resolved support cases.")
        return documents

    def _normalize_case(self, case: SupportCaseSchema) -> Document:
        """Normalizes a resolved case into a standard indexable text document."""
        # Clean spacing
        q = case.question.strip()
        a = case.answer.strip()

        # Build indexable content representing this case
        normalized_content = (
            f"Category: {case.category}\n"
            f"Question: {q}\n"
            f"Answer: {a}"
        )

        # Build metadata dictionary
        metadata = {
            "document_id": case.case_id,
            "case_id": case.case_id,
            "category": case.category,
            "source": self.file_path,
            "priority": case.priority,
            "type": "resolved_case",
            **case.metadata
        }

        return Document(
            id=case.case_id,
            content=normalized_content,
            metadata=metadata
        )
