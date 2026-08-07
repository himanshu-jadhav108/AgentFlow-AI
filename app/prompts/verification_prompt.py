"""Verification prompt template for checking answer truthfulness."""

VERIFICATION_PROMPT_TEMPLATE = (
    "Factual Context Chunks:\n"
    "{context}\n\n"
    "Proposed Answer to Verify:\n"
    "{answer}\n\n"
    "Instructions:\n"
    "Compare the Proposed Answer against the Factual Context Chunks.\n"
    "Verify whether the proposed answer is completely supported by the factual chunks without adding extra claims, "
    "assumptions, or hallucinated facts.\n\n"
    "Your output MUST be a valid JSON object with the following structure:\n"
    "{{\n"
    '  "supported": true or false,\n'
    '  "reason": "Detailed analysis explaining why it is supported or unsupported"\n'
    "}}\n"
)
