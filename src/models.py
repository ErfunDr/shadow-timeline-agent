from pydantic import BaseModel, Field


class SourceDocument(BaseModel):
    filename: str
    content: str


class TimelineEvent(BaseModel):
    date: str = "Unknown"
    title: str
    summary: str
    importance: int = Field(ge=1, le=10)
    suspicious_score: int = Field(ge=1, le=10)
    sources: list[str] = []
    evidence: str | None = ""


class Entity(BaseModel):
    name: str
    type: str
    description: str = ""
    role_in_case: str = ""
    importance: int = Field(default=5, ge=1, le=10)
    source: str = ""
    evidence: str | None = ""


class Connection(BaseModel):
    from_entity: str
    relationship: str
    to_entity: str
    evidence: str | None = ""
    source: str = ""


class InvestigationReport(BaseModel):
    main_topic: str
    short_summary: str
    source_count: int
    timeline: list[TimelineEvent] = []
    facts: list[str] = []
    open_questions: list[str] = []
    entities: list[Entity] = []
    connections: list[Connection] = []
    possible_contradictions: list[str] = []
    final_assessment: str = ""