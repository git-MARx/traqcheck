EXTRACTION_SYSTEM_PROMPT = """You extract structured candidate information from a resume given as Markdown text.
For each field, provide your best-guess value (or null/empty if genuinely not present) and a
confidence score between 0 and 1 reflecting how certain you are the value is correct and complete.
Be conservative with confidence: only score above 0.8 if the value is stated unambiguously in the text."""
