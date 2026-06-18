from pathlib import Path
from rich.console import Console

from models import SourceDocument
from entity_extractor import extract_entities
from connection_extractor import extract_connections
from report_builder import save_investigation_report

console = Console()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"


def read_sources() -> list[SourceDocument]:
    files = sorted(DATA_DIR.glob("article*.txt"))

    if not files:
        raise FileNotFoundError("No article files found in data folder.")

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

    return sources


def main() -> None:
    console.print("[bold cyan]Shadow Investigation Agent V4[/bold cyan]")

    sources = read_sources()
    console.print(f"[cyan]Loaded {len(sources)} sources.[/cyan]")

    entities = extract_entities(sources)
    console.print(f"[green]Extracted {len(entities)} entities.[/green]")

    connections = extract_connections(sources, entities)
    console.print(f"[green]Extracted {len(connections)} connections.[/green]")

    json_path, md_path = save_investigation_report(
        entities=entities,
        connections=connections,
        output_dir=OUTPUT_DIR
    )

    console.print("[green]Done.[/green]")
    console.print(f"JSON: {json_path}")
    console.print(f"Markdown: {md_path}")


if __name__ == "__main__":
    main()