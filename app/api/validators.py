"""Request validators for query sanitization and traversal prevention."""

import re
from fastapi import HTTPException, status
from core.logger import logger


class RequestValidator:
    """Validator class providing static validation methods for REST payloads."""

    @staticmethod
    def validate_question(question: str) -> str:
        """Sanitizes search queries, checking lengths and blocking injections.

        Args:
            question: User's input question.

        Returns:
            str: Cleaned, sanitized question string.

        Raises:
            HTTPException: 400 Bad Request error if input violates safety policies.
        """
        if not question or not str(question).strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request question field cannot be empty.",
            )

        cleaned = str(question).strip()

        # 1. Length constraints check
        if len(cleaned) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question is too short (minimum 3 characters required).",
            )

        if len(cleaned) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question exceeds maximum payload size of 1000 characters.",
            )

        # 2. Path traversal attack check
        path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"/etc/passwd",
            r"c:\\windows",
            r"/etc/hosts",
        ]
        for pattern in path_traversal_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                logger.warning(f"Security Warning: Blocked path traversal attempt in query: '{cleaned}'")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Dangerous file system or path traversal sequence detected.",
                )

        # 3. HTML/Script Injection sanitization
        cleaned = re.sub(r"<script.*?>.*?</script>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]*>", "", cleaned)  # Remove raw html tags

        return cleaned
