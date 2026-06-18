import json
import re
import requests

from models import Entity, SourceDocument

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"
MAX_TIMEOUT_SECONDS = 180


def extract_json(raw_text: str) -> list:
    match = re.search(r"\[.*\]", raw_text, re.DOTALL)

    if not match:
        raise ValueError("No JSON list found in model response.")

    return json.loads(match.group(0))


def extract_entities(sources: list[SourceDocument]) -> list[Entity]:
    source_text = ""

    for source in sources:
        source_text += f"\nSOURCE: {source.filename}\n{source.content}\n"

    prompt = f"""
You are an AI entity extraction system.

Extract important entities from the sources.

Return ONLY valid JSON list.

Each item must have:
name
type
description
role_in_case
importance
source
evidence

Rules:
- No markdown
- No comments
- Use only provided sources
- importance must be between 1 and 10

Sources:
{source_text}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=MAX_TIMEOUT_SECONDS
    )

    response.raise_for_status()

    raw_output = response.json()["response"]

    print("RAW ENTITY OUTPUT:")
    print(raw_output)

    data = extract_json(raw_output)

    return [Entity(**item) for item in data]