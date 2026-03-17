"""Pydantic data models for LABLOG."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EntryStatus(str, Enum):
    """Status of a lab entry."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ExperimentStatus(str, Enum):
    """Status of an experiment."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LabEntry(BaseModel):
    """A structured lab notebook entry."""

    id: UUID = Field(default_factory=uuid4)
    title: str
    hypothesis: str = ""
    procedure: str = ""
    observations: str = ""
    results: str = ""
    conclusions: str = ""
    tags: list[str] = Field(default_factory=list)
    status: EntryStatus = EntryStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    experiment_ids: list[UUID] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def is_complete(self) -> bool:
        """Check whether all structured fields are filled in."""
        return all([
            self.hypothesis,
            self.procedure,
            self.observations,
            self.results,
            self.conclusions,
        ])


class Metric(BaseModel):
    """A single recorded metric value."""

    name: str
    value: float
    unit: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)


class Artifact(BaseModel):
    """Reference to an experiment artifact (file, plot, dataset)."""

    name: str
    path: str
    artifact_type: str = "file"
    description: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class Experiment(BaseModel):
    """An experiment with parameters, metrics, and artifacts."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    metrics: list[Metric] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    status: ExperimentStatus = ExperimentStatus.PLANNED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def log_metric(self, name: str, value: float, unit: str = "") -> Metric:
        """Record a metric value for this experiment."""
        metric = Metric(name=name, value=value, unit=unit)
        self.metrics.append(metric)
        return metric

    def add_artifact(
        self, name: str, path: str, artifact_type: str = "file", description: str = ""
    ) -> Artifact:
        """Attach an artifact to this experiment."""
        artifact = Artifact(
            name=name, path=path, artifact_type=artifact_type, description=description
        )
        self.artifacts.append(artifact)
        return artifact

    def get_metric_values(self, name: str) -> list[float]:
        """Return all recorded values for a given metric name."""
        return [m.value for m in self.metrics if m.name == name]


class ProtocolStep(BaseModel):
    """A single step in a protocol."""

    order: int
    instruction: str
    duration_minutes: float | None = None
    notes: str = ""


class Protocol(BaseModel):
    """A reusable experiment protocol template."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    steps: list[ProtocolStep] = Field(default_factory=list)
    required_materials: list[str] = Field(default_factory=list)
    required_equipment: list[str] = Field(default_factory=list)
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)

    @property
    def total_duration_minutes(self) -> float:
        """Calculate total estimated duration from steps."""
        return sum(s.duration_minutes for s in self.steps if s.duration_minutes)


class Dataset(BaseModel):
    """A reference to experimental data."""

    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    source: str = ""
    columns: list[str] = Field(default_factory=list)
    row_count: int = 0
    file_path: str = ""
    experiment_id: UUID | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
