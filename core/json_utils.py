import re
import json


def extract_json(text):
    """Extract JSON from LLM response, handling markdown blocks."""
    if "```" in text:
        match = re.search(r"```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    match = re.search(r"(\[.*\]|\{.*\})", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return None
