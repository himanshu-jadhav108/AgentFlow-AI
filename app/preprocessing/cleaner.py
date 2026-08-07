"""Text cleaning preprocessing module for cleaning document content."""

import re
import unicodedata
from core.logger import logger


class TextCleaner:
    """Cleaner for normalizing text characters, whitespaces, and newlines."""

    def clean(self, text: str) -> str:
        """Cleans document text: unicode normalization, newline reduction, space collapses.

        Ensures markdown lists, headings, and code block spacing are preserved.

        Args:
            text: Raw input string.

        Returns:
            str: Cleaned and normalized string.
        """
        if not text:
            return ""

        # Unicode NFKC normalization
        cleaned = unicodedata.normalize("NFKC", text)

        # Split on code blocks (triple backticks) to protect code block spacing
        parts = re.split(r"(```[\s\S]*?```)", cleaned)

        cleaned_parts = []
        for part in parts:
            if part.startswith("```") and part.endswith("```"):
                # Preserve code blocks completely unchanged
                cleaned_parts.append(part)
            else:
                # Process regular text
                # Normalize line-by-line: collapse multiple spaces/tabs, strip trailing whitespace
                lines = part.split("\n")
                processed_lines = []
                for line in lines:
                    # Collapse multiple inline spaces and tabs into a single space
                    collapsed = re.sub(r"[ \t]+", " ", line)
                    # Strip only trailing whitespace, keep indentation (e.g. lists, markdown blockquotes)
                    processed_lines.append(collapsed.rstrip())

                cleaned_part = "\n".join(processed_lines)
                # Collapse 3 or more consecutive newlines to exactly 2 (preserves paragraph breaks)
                cleaned_part = re.sub(r"\n{3,}", "\n\n", cleaned_part)
                cleaned_parts.append(cleaned_part)

        final_text = "".join(cleaned_parts).strip()
        logger.debug(f"Cleaned text: reduced length from {len(text)} to {len(final_text)} characters.")
        return final_text
