from pathlib import Path
from rich.console import Console

from models import SourceDocument
from entity_extractor import extract_entities
from connection_extractor import extract_connections
from graph_builder import build_graph
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


def save_json(path: Path, data: dict):
    path.write_text(
        __import__("json").dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def main():
    console.print("[bold cyan]Shadow Investigation Agent V5[/bold cyan]")

    sources = read_sources()
    console.print(f"[cyan]Loaded {len(sources)} sources.[/cyan]")

    # 1. Entities
    entities = extract_entities(sources)
    console.print(f"[green]Extracted {len(entities)} entities.[/green]")

    # 2. Connections
    connections = extract_connections(sources, entities)
    console.print(f"[green]Extracted {len(connections)} connections.[/green]")

    # 3. Graph
    graph = build_graph(entities, connections)

    # 4. Paths
    json_entities_path = OUTPUT_DIR / "entities.json"
    json_connections_path = OUTPUT_DIR / "connections.json"
    json_graph_path = OUTPUT_DIR / "graph.json"

    OUTPUT_DIR.mkdir(exist_ok=True)

    # 5. Save outputs
    save_json(json_entities_path, [e.model_dump() for e in entities])
    save_json(json_connections_path, [c.model_dump() for c in connections])
    save_json(json_graph_path, graph)

    # 6. Report (for YouTube)
    _, md_path = save_investigation_report(
        entities=entities,
        connections=connections,
        output_dir=OUTPUT_DIR
    )

    console.print("[bold green]DONE ✅[/bold green]")
    console.print(f"Graph: {json_graph_path}")
    console.print(f"Entities: {json_entities_path}")
    console.print(f"Connections: {json_connections_path}")
    console.print(f"Report: {md_path}")


if __name__ == "__main__":
    main()