"""Answer generation manager coordinating prompts, local model runs, and parsing."""

from typing import Any, Dict, List

from app.generation.formatter import parse_json_response
from app.llm.inference import InferenceManager
from app.prompts.generation_prompt import GENERATION_PROMPT_TEMPLATE
from app.prompts.system_prompt import SYSTEM_PROMPT
from core.logger import logger


class AnswerGenerator:
    """Orchestrator for prompt formulation and local model queries."""

    def __init__(self) -> None:
        from app.core.registry import dependency_container

        self.inference_manager = dependency_container.get_llm()

    def generate(
        self,
        question: str,
        retrieved_chunks: List[Any],
        conversation_history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Builds context prompts, triggers LLM inference, and parses response structures.

        Args:
            question: User support question.
            retrieved_chunks: List of RetrievedChunk instances.
            conversation_history: List of role/content conversation histories.

        Returns:
            Dict[str, Any]: Parsed response dictionary containing answer, citations, and reasoning.
        """
        logger.info("AnswerGenerator: Formulating prompt for local LLM...")

        # 1. Format document context
        context_parts = []
        for chunk in retrieved_chunks:
            source_name = getattr(chunk, "source", "Unknown Source")
            chunk_id = getattr(chunk, "chunk_id", "Unknown ID")
            text = getattr(chunk, "text", "")
            context_parts.append(
                f"Document Name: {source_name} (Chunk ID: {chunk_id})\nPassage: {text}"
            )

        context_str = (
            "\n\n".join(context_parts)
            if context_parts
            else "No relevant documents retrieved."
        )

        # 2. Format conversation history
        history_parts = []
        for msg in conversation_history:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            history_parts.append(f"{role}: {content}")

        history_str = (
            "\n".join(history_parts)
            if history_parts
            else "No previous conversation history."
        )

        # 3. Format Generation Prompt template
        user_prompt = GENERATION_PROMPT_TEMPLATE.format(
            context=context_str,
            history=history_str,
            question=question,
        )

        # 4. Integrate system rules and compile full prompt
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        # 5. Query the local LLM
        raw_output = self.inference_manager.generate_text(full_prompt)

        # 6. Parse and validate JSON structure
        try:
            parsed = parse_json_response(raw_output)

            # Ensure all required JSON fields are present
            if "answer" not in parsed:
                parsed["answer"] = "I couldn't find supporting information."
            if "citations" not in parsed:
                parsed["citations"] = []
            if "reason" not in parsed:
                parsed["reason"] = "Generated from document contexts."

            return parsed
        except Exception as e:
            logger.error(f"Model response formatting error: {e}")
            raise e
