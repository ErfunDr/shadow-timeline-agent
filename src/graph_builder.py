from models import Entity, Connection


def normalize_id(text: str) -> str:
    return text.lower().replace(" ", "_").replace("-", "_")


def build_graph(entities: list[Entity], connections: list[Connection]) -> dict:
    node_map = {}

    for entity in entities:
        node_id = normalize_id(entity.name)

        node_map[node_id] = {
            "id": node_id,
            "label": entity.name,
            "type": entity.type,
            "importance": entity.importance
        }

    edges = []

    for conn in connections:
        source_id = normalize_id(conn.from_entity)
        target_id = normalize_id(conn.to_entity)

        if source_id not in node_map:
            node_map[source_id] = {
                "id": source_id,
                "label": conn.from_entity,
                "type": "Unknown",
                "importance": 5
            }

        if target_id not in node_map:
            node_map[target_id] = {
                "id": target_id,
                "label": conn.to_entity,
                "type": "Unknown",
                "importance": 5
            }

        edges.append({
            "from": source_id,
            "to": target_id,
            "label": conn.relationship,
            "context": conn.evidence,
            "source": conn.source
        })

    return {
        "nodes": list(node_map.values()),
        "edges": edges
    }