import json
import re
from pathlib import Path
from datetime import datetime

import requests
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

console = Console()

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "input.txt"
OUTPUT_DIR = BASE_DIR / "outputs"

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


class TimelineEvent(BaseModel):
    date: str = Field(description="Date of the event")
    title: str = Field(description="Short event title")
    summary: str = Field(description="What happened")
    importance: int = Field(description="Importance score from 1 to 10")
    suspicious_score: int = Field(description="Suspicion score from 1 to 10")
    evidence: str = Field(description="Evidence from the input text")


class InvestigationReport(BaseModel):
    main_topic: str
    short_summary: str
    timeline: list[TimelineEvent]
    mystery_angle: str
    open_questions: list[str]
    final_assessment: str


def read_input() -> str:
    text = INPUT_FILE.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError("data/input.txt is empty.")

    return text


def extract_json(raw_text: str) -> dict:
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)

    if not match:
        raise ValueError("No JSON object found in model response.")

    json_text = match.group(0)
    return json.loads(json_text)


def ask_ollama(text: str) -> InvestigationReport:
    prompt = f"""
You are an AI detective and investigation analyst.

Analyze the following text and return ONLY valid JSON.

Do not write markdown.
Do not write explanations outside JSON.
Do not invent facts.
Use only the provided text.

Return ONLY valid JSON.

Required keys:

main_topic
short_summary
timeline
mystery_angle
open_questions
final_assessment

Timeline items must contain:

date
title
summary
importance
suspicious_score
evidence

Rules:
- Valid JSON only
- No markdown
- No comments
- Use double quotes
- Dates must be YYYY-MM-DD or Unknown
- importance between 1 and 10
- suspicious_score between 1 and 10

Text:
{text}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    raw_output = response.json()["response"]
    
    print("RAW MODEL OUTPUT:")
    print(raw_output)
    
    data = extract_json(raw_output)

    return InvestigationReport(**data)


def save_json(report: InvestigationReport, timestamp: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)

    json_path = OUTPUT_DIR / f"timeline_report_{timestamp}.json"

    json_path.write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return json_path


def save_markdown(report: InvestigationReport, timestamp: str) -> Path:
    md_path = OUTPUT_DIR / f"timeline_report_{timestamp}.md"

    markdown = f"# {report.main_topic}\n\n"
    markdown += f"## Short Summary\n\n{report.short_summary}\n\n"
    markdown += f"## Mystery Angle\n\n{report.mystery_angle}\n\n"
    markdown += "## Timeline\n\n"

    for event in report.timeline:
        markdown += f"### {event.date} — {event.title}\n\n"
        markdown += f"{event.summary}\n\n"
        markdown += f"- Importance: {event.importance}/10\n"
        markdown += f"- Suspicious Score: {event.suspicious_score}/10\n"
        markdown += f"- Evidence: {event.evidence}\n\n"

    markdown += "## Open Questions\n\n"

    for question in report.open_questions:
        markdown += f"- {question}\n"

    markdown += f"\n## Final Assessment\n\n{report.final_assessment}\n"

    md_path.write_text(markdown, encoding="utf-8")

    return md_path


def main() -> None:
    console.print("[bold cyan]Shadow Timeline Agent V2[/bold cyan]")

    try:
        text = read_input()
        report = ask_ollama(text)

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