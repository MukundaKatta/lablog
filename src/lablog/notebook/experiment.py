"""Experiment tracking with parameters, metrics, and artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from lablog.models import Experiment, ExperimentStatus, Metric


class ExperimentTracker:
    """Tracks experiments with their parameters, metrics, and artifacts."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir) if storage_dir else Path(".lablog_data/experiments")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._experiments: dict[UUID, Experiment] = {}
        self._load_experiments()

    def _load_experiments(self) -> None:
        """Load all experiments from disk."""
        for path in self.storage_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                exp = Experiment.model_validate(data)
                self._experiments[exp.id] = exp
            except (json.JSONDecodeError, ValueError):
                continue

    def _save_experiment(self, experiment: Experiment) -> Path:
        """Persist a single experiment to disk."""
        path = self.storage_dir / f"{experiment.id}.json"
        path.write_text(experiment.model_dump_json(indent=2))
        return path

    def create(
        self,
        name: str,
        description: str = "",
        parameters: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> Experiment:
        """Create a new experiment."""
        experiment = Experiment(
            name=name,
            description=description,
            parameters=parameters or {},
            tags=tags or [],
        )
        self._experiments[experiment.id] = experiment
        self._save_experiment(experiment)
        return experiment

    def get(self, experiment_id: UUID) -> Experiment | None:
        """Retrieve an experiment by ID."""
        return self._experiments.get(experiment_id)

    def start(self, experiment_id: UUID) -> Experiment | None:
        """Mark an experiment as running."""
        exp = self._experiments.get(experiment_id)
        if exp is None:
            return None
        exp.status = ExperimentStatus.RUNNING
        exp.started_at = datetime.now()
        self._save_experiment(exp)
        return exp

    def complete(self, experiment_id: UUID) -> Experiment | None:
        """Mark an experiment as completed."""
        exp = self._experiments.get(experiment_id)
        if exp is None:
            return None
        exp.status = ExperimentStatus.COMPLETED
        exp.completed_at = datetime.now()
        self._save_experiment(exp)
        return exp

    def fail(self, experiment_id: UUID) -> Experiment | None:
        """Mark an experiment as failed."""
        exp = self._experiments.get(experiment_id)
        if exp is None:
            return None
        exp.status = ExperimentStatus.FAILED
        exp.completed_at = datetime.now()
        self._save_experiment(exp)
        return exp

    def log_metric(
        self, experiment_id: UUID, name: str, value: float, unit: str = ""
    ) -> Metric | None:
        """Log a metric for an experiment."""
        exp = self._experiments.get(experiment_id)
        if exp is None:
            return None
        metric = exp.log_metric(name, value, unit)
        self._save_experiment(exp)
        return metric

    def add_artifact(
        self,
        experiment_id: UUID,
        name: str,
        path: str,
        artifact_type: str = "file",
        description: str = "",
    ) -> bool:
        """Add an artifact to an experiment."""
        exp = self._experiments.get(experiment_id)
        if exp is None:
            return False
        exp.add_artifact(name, path, artifact_type, description)
        self._save_experiment(exp)
        return True

    def list_experiments(
        self,
        status: ExperimentStatus | None = None,
        tags: list[str] | None = None,
    ) -> list[Experiment]:
        """List experiments with optional filtering."""
        experiments = list(self._experiments.values())
        if status is not None:
            experiments = [e for e in experiments if e.status == status]
        if tags:
            tag_set = set(tags)
            experiments = [e for e in experiments if tag_set.intersection(e.tags)]
        return sorted(experiments, key=lambda e: e.created_at, reverse=True)

    def compare_experiments(
        self, experiment_ids: list[UUID], metric_name: str
    ) -> dict[str, list[float]]:
        """Compare a specific metric across multiple experiments."""
        comparison: dict[str, list[float]] = {}
        for eid in experiment_ids:
            exp = self._experiments.get(eid)
            if exp is not None:
                values = exp.get_metric_values(metric_name)
                comparison[exp.name] = values
        return comparison

    @property
    def count(self) -> int:
        """Return total number of tracked experiments."""
        return len(self._experiments)
