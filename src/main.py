import json
import re
from pathlib import Path
from datetime import datetime

import requests
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

console = Console()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


class SourceDocument(BaseModel):
    filename: str
    content: str


class TimelineEvent(BaseModel):
    date: str = Field(description="YYYY-MM-DD or Unknown")
    title: str
    summary: str
    importance: int
    suspicious_score: int
    sources: list[str]
    evidence: str | None = ""


class InvestigationReport(BaseModel):
    main_topic: str
    short_summary: str
    source_count: int
    timeline: list[TimelineEvent]
    key_connections: list[str]
    possible_contradictions: list[str]
    mystery_angle: str
    open_questions: list[str]
    final_assessment: str


def read_sources() -> list[SourceDocument]:
    files = sorted(DATA_DIR.glob("article*.txt"))

    if not files:
        raise FileNotFoundError("No article files found. Add article1.txt, article2.txt, article3.txt inside data/.")

    sources = []

    for file in files:
        text = file.read_text(encoding="utf-8").strip()

        if text:
            sources.append(
                SourceDocument(
                    filename=file.name,
                    content=text
                )
            )

    if not sources:
        raise ValueError("All article files are empty.")

    return sources


def build_source_block(sources: list[SourceDocument]) -> str:
    blocks = []

    for source in sources:
        blocks.append(
            f"SOURCE: {source.filename}\n{source.content}"
        )

    return "\n\n---\n\n".join(blocks)


def extract_json(raw_text: str) -> dict:
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found in model response.")

    json_text = match.group(0)
    return json.loads(json_text)


def ask_ollama(sources: list[SourceDocument]) -> InvestigationReport:
    source_block = build_source_block(sources)

    prompt = f"""
You are an AI detective and multi-source investigation analyst.

Analyze the sources below and create a structured investigation report.

Return ONLY valid JSON.

Required keys:
main_topic
short_summary
source_count
timeline
key_connections
possible_contradictions
mystery_angle
open_questions
final_assessment

Each timeline item must include:
date
title
summary
importance
suspicious_score
sources
evidence

Rules:
- Use only the provided sources.
- Do not invent facts.
- Valid JSON only.
- No markdown.
- No comments.
- Use double quotes.
- Dates must be YYYY-MM-DD or Unknown.
- If an exact date is not present, use Unknown.
- importance must be between 1 and 10.
- suspicious_score must be between 1 and 10.
- sources must be a list of filenames.
- source_count must equal the number of source files.
- possible_contradictions can be an empty list if none are found.
- final_assessment must not be empty.

Sources:

{source_block}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=180
    )

    response.raise_for_status()

    raw_output = response.json()["response"]

    print("RAW MODEL OUTPUT:")
    print(raw_output)

    data = extract_json(raw_output)

    return InvestigationReport(**data)


def save_json(report: InvestigationReport, timestamp: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)

    json_path = OUTPUT_DIR / f"multi_source_report_{timestamp}.json"

    json_path.write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return json_path


def save_markdown(report: InvestigationReport, timestamp: str) -> Path:
    md_path = OUTPUT_DIR / f"multi_source_report_{timestamp}.md"

    markdown = f"# {report.main_topic}\n\n"
    markdown += f"## Short Summary\n\n{report.short_summary}\n\n"
    markdown += f"## Sources Analyzed\n\n{report.source_count}\n\n"

    markdown += "## Timeline\n\n"

    for event in report.timeline:
        markdown += f"### {event.date} — {event.title}\n\n"
        markdown += f"{event.summary}\n\n"
        markdown += f"- Importance: {event.importance}/10\n"
        markdown += f"- Suspicious Score: {event.suspicious_score}/10\n"
        markdown += f"- Sources: {', '.join(event.sources)}\n"
        markdown += f"- Evidence: {event.evidence or 'No direct evidence extracted'}\n\n"

    markdown += "## Key Connections\n\n"

    for item in report.key_connections:
        markdown += f"- {item}\n"

    markdown += "\n## Possible Contradictions\n\n"

    if report.possible_contradictions:
        for item in report.possible_contradictions:
            markdown += f"- {item}\n"
    else:
        markdown += "- No clear contradictions found.\n"

    markdown += f"\n## Mystery Angle\n\n{report.mystery_angle}\n\n"

    markdown += "## Open Questions\n\n"

    for question in report.open_questions:
        markdown += f"- {question}\n"

    markdown += f"\n## Final Assessment\n\n{report.final_assessment}\n"

    md_path.write_text(markdown, encoding="utf-8")

    return md_path


def main() -> None:
    console.print("[bold cyan]Shadow Timeline Agent V3[/bold cyan]")

    try:
        sources = read_sources()
        console.print(f"[cyan]Loaded {len(sources)} sources.[/cyan]")

        report = ask_ollama(sources)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        json_path = save_json(report, timestamp)
        md_path = save_markdown(report, timestamp)

        console.print("[green]Done.[/green]")
        console.print(f"[green]JSON:[/green] {json_path}")
        console.print(f"[green]Markdown:[/green] {md_path}")

    except requests.exceptions.ConnectionError:
        console.print("[red]Error: Ollama is not running.[/red]")
        console.print("Run this first: ollama run llama3.2")

    except (ValueError, json.JSONDecodeError, ValidationError) as error:
        console.print("[red]Error: Could not parse model output as valid JSON.[/red]")
        console.print(error)

    except Exception as error:
        console.print("[red]Unexpected error:[/red]")
        console.print(error)


if __name__ == "__main__":
    main()