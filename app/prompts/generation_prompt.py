"""Answer generation prompt template injecting context and schema constraints."""

GENERATION_PROMPT_TEMPLATE = (
    "Context Documents:\n"
    "{context}\n\n"
    "Conversation History:\n"
    "{history}\n\n"
    "Question: {question}\n\n"
    "Instructions:\n"
    "Answer the specific user question above using ONLY facts explicitly stated in the context documents. "
    "If the context documents do not contain enough information to answer, set the 'answer' field to "
    '"I couldn\'t find supporting information." and "citations" to [].\n\n'
    "CRITICAL FORMAT RULES:\n"
    "1. Your output MUST be ONLY a single raw JSON object starting with '{{' and ending with '}}'.\n"
    "2. DO NOT output any introductory text, preambles, or markdown headings.\n"
    "3. You MUST include the exact Document Name(s) (e.g. 'faq.md') in the 'citations' JSON array for any answer provided.\n\n"
    "JSON Schema:\n"
    "{{\n"
    '  "answer": "Answer string addressing the user question based ONLY on the context",\n'
    '  "citations": ["Exact Document Name from context documents, e.g. faq.md"],\n'
    '  "reason": "Reasoning justifying how the context supports the answer"\n'
    "}}\n"
)
