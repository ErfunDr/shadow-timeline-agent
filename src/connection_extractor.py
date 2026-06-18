import json
import re
import requests

from models import Connection, Entity, SourceDocument

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"
MAX_TIMEOUT_SECONDS = 180


def extract_json(raw_text: str) -> list:
    match = re.search(r"\[.*\]", raw_text, re.DOTALL)

    if not match:
        raise ValueError("No JSON list found in model response.")

    return json.loads(match.group(0))


def extract_connections(
    sources: list[SourceDocument],
    entities: list[Entity]
) -> list[Connection]:
    source_text = ""

    for source in sources:
        source_text += f"\nSOURCE: {source.filename}\n{source.content}\n"

    entity_names = [entity.name for entity in entities]

    prompt = f"""
You are an AI relationship extraction system.

Extract relationships between the entities based only on the sources.

Known entities:
{entity_names}

Return ONLY valid JSON list.

Each item must have:
from_entity
relationship
to_entity
evidence
source

Rules:
- No markdown
- No comments
- Use only provided sources
- Be careful with direction. If Binance withdrew from the FTX deal, from_entity should be Binance and to_entity should be FTX.
- Only use entity names from the known entities list
- relationship should be short, like "founded", "created", "withdrew from", "connected to"

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

    print("RAW CONNECTION OUTPUT:")
    print(raw_output)

    data = extract_json(raw_output)

    return [Connection(**item) for item in data]


