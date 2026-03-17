"""Protocol templates for reproducible experiment procedures."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from lablog.models import Experiment, Protocol, ProtocolStep


class ProtocolTemplate:
    """Manages reusable protocol templates for reproducible experiments."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir) if storage_dir else Path(".lablog_data/protocols")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._protocols: dict[UUID, Protocol] = {}
        self._load_protocols()

    def _load_protocols(self) -> None:
        """Load all protocols from disk."""
        for path in self.storage_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                protocol = Protocol.model_validate(data)
                self._protocols[protocol.id] = protocol
            except (json.JSONDecodeError, ValueError):
                continue

    def _save_protocol(self, protocol: Protocol) -> Path:
        """Persist a protocol to disk."""
        path = self.storage_dir / f"{protocol.id}.json"
        path.write_text(protocol.model_dump_json(indent=2))
        return path

    def create(
        self,
        name: str,
        description: str = "",
        steps: list[dict[str, object]] | None = None,
        required_materials: list[str] | None = None,
        required_equipment: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> Protocol:
        """Create a new protocol template."""
        protocol_steps = []
        if steps:
            for i, step_data in enumerate(steps):
                protocol_steps.append(
                    ProtocolStep(order=i + 1, **step_data)  # type: ignore[arg-type]
                )

        protocol = Protocol(
            name=name,
            description=description,
            steps=protocol_steps,
            required_materials=required_materials or [],
            required_equipment=required_equipment or [],
            tags=tags or [],
        )
        self._protocols[protocol.id] = protocol
        self._save_protocol(protocol)
        return protocol

    def get(self, protocol_id: UUID) -> Protocol | None:
        """Retrieve a protocol by ID."""
        return self._protocols.get(protocol_id)

    def update(self, protocol_id: UUID, **fields: object) -> Protocol | None:
        """Update fields of an existing protocol."""
        protocol = self._protocols.get(protocol_id)
        if protocol is None:
            return None
        for key, value in fields.items():
            if hasattr(protocol, key):
                setattr(protocol, key, value)
        protocol.updated_at = datetime.now()
        self._save_protocol(protocol)
        return protocol

    def add_step(
        self,
        protocol_id: UUID,
        instruction: str,
        duration_minutes: float | None = None,
        notes: str = "",
    ) -> Protocol | None:
        """Add a step to an existing protocol."""
        protocol = self._protocols.get(protocol_id)
        if protocol is None:
            return None
        next_order = max((s.order for s in protocol.steps), default=0) + 1
        step = ProtocolStep(
            order=next_order,
            instruction=instruction,
            duration_minutes=duration_minutes,
            notes=notes,
        )
        protocol.steps.append(step)
        protocol.updated_at = datetime.now()
        self._save_protocol(protocol)
        return protocol

    def delete(self, protocol_id: UUID) -> bool:
        """Delete a protocol by ID."""
        if protocol_id not in self._protocols:
            return False
        del self._protocols[protocol_id]
        path = self.storage_dir / f"{protocol_id}.json"
        if path.exists():
            path.unlink()
        return True

    def instantiate_experiment(
        self, protocol_id: UUID, experiment_name: str, **extra_params: object
    ) -> Experiment | None:
        """Create an Experiment pre-populated from a protocol template."""
        protocol = self._protocols.get(protocol_id)
        if protocol is None:
            return None
        params = {
            "protocol_id": str(protocol.id),
            "protocol_name": protocol.name,
            "protocol_version": protocol.version,
            "steps": [s.instruction for s in protocol.steps],
            "materials": protocol.required_materials,
            "equipment": protocol.required_equipment,
            **extra_params,
        }
        return Experiment(
            name=experiment_name,
            description=f"Experiment from protocol: {protocol.name}",
            parameters=params,
            tags=protocol.tags.copy(),
        )

    def list_protocols(self, tags: list[str] | None = None) -> list[Protocol]:
        """List all protocols, optionally filtered by tags."""
        protocols = list(self._protocols.values())
        if tags:
            tag_set = set(tags)
            protocols = [p for p in protocols if tag_set.intersection(p.tags)]
        return sorted(protocols, key=lambda p: p.created_at, reverse=True)

    @property
    def count(self) -> int:
        """Return total number of protocols."""
        return len(self._protocols)
