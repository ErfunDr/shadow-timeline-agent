import json
from pathlib import Path
from datetime import datetime

from models import Entity, Connection


def save_investigation_report(
    entities: list[Entity],
    connections: list[Connection],
    output_dir: Path
) -> tuple[Path, Path]:
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = output_dir / f"investigation_graph_{timestamp}.json"
    md_path = output_dir / f"investigation_graph_{timestamp}.md"

    json_data = {
        "entities": [entity.model_dump() for entity in entities],
        "connections": [connection.model_dump() for connection in connections],
    }

    json_path.write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    markdown = "# Investigation Graph Report\n\n"

    markdown += "## Entities\n\n"

    for entity in entities:
        markdown += f"### {entity.name}\n\n"
        markdown += f"- Type: {entity.type}\n"
        markdown += f"- Importance: {entity.importance}/10\n"
        markdown += f"- Source: {entity.source}\n"
        markdown += f"- Role: {entity.role_in_case}\n"
        markdown += f"- Description: {entity.description}\n"
        markdown += f"- Evidence: {entity.evidence or 'No evidence extracted'}\n\n"

    markdown += "## Connections\n\n"

    if connections:
        for connection in connections:
            markdown += (
                f"- **{connection.from_entity}** "
                f"-- {connection.relationship} --> "
                f"**{connection.to_entity}**\n"
            )
            markdown += f"  - Source: {connection.source}\n"
            markdown += f"  - Evidence: {connection.evidence or 'No evidence extracted'}\n\n"
    else:
        markdown += "No connections extracted.\n"

    md_path.write_text(markdown, encoding="utf-8")

    return json_path, md_path