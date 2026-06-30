from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel

class Run(SQLModel, table=True):
    id: str = Field(primary_key=True)
    task: str
    status: str = Field(default="running")
    outcome: Optional[str] = None
    total_tokens: int = Field(default=0)
    total_cost_usd: float = Field(default=0.0)
    total_latency_ms: float = Field(default=0.0)
    agent_count: int = Field(default=0)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    metadata_json: Optional[str] = None

class Span(SQLModel, table=True):
    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    parent_span_id: Optional[str] = None
    agent_id: Optional[str] = None
    agent_role: Optional[str] = None
    span_type: str = Field(index=True)
    model: Optional[str] = None
    input_content: Optional[str] = None
    output_content: Optional[str] = None
    tokens_in: int = Field(default=0)
    tokens_out: int = Field(default=0)
    latency_ms: float = Field(default=0.0)
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

class Diagnosis(SQLModel, table=True):
    id: str = Field(primary_key=True)
    run_id: str = Field(index=True)
    failure_category: str
    failure_mode: str = Field(index=True)
    confidence: float
    root_cause: str
    suggested_fix: str
    evidence_span_ids: str # JSON array
    diagnosed_at: datetime = Field(default_factory=datetime.utcnow)

class Cluster(SQLModel, table=True):
    id: str = Field(primary_key=True)
    representative_cause: str
    failure_mode: str
    count: int = Field(default=1)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    diagnosis_ids: str # JSON array
