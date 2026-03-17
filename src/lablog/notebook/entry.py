"""Lab entry management with structured fields."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from lablog.models import EntryStatus, LabEntry


class LabEntryManager:
    """Manages creation, storage, and retrieval of lab notebook entries."""

    def __init__(self, storage_dir: str | Path | None = None) -> None:
        self.storage_dir = Path(storage_dir) if storage_dir else Path(".lablog_data/entries")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._entries: dict[UUID, LabEntry] = {}
        self._load_entries()

    def _load_entries(self) -> None:
        """Load all entries from disk."""
        for path in self.storage_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                entry = LabEntry.model_validate(data)
                self._entries[entry.id] = entry
            except (json.JSONDecodeError, ValueError):
                continue

    def _save_entry(self, entry: LabEntry) -> Path:
        """Persist a single entry to disk."""
        path = self.storage_dir / f"{entry.id}.json"
        path.write_text(entry.model_dump_json(indent=2))
        return path

    def create(
        self,
        title: str,
        hypothesis: str = "",
        procedure: str = "",
        observations: str = "",
        results: str = "",
        conclusions: str = "",
        tags: list[str] | None = None,
    ) -> LabEntry:
        """Create a new lab entry with structured fields."""
        entry = LabEntry(
            title=title,
            hypothesis=hypothesis,
            procedure=procedure,
            observations=observations,
            results=results,
            conclusions=conclusions,
            tags=tags or [],
        )
        self._entries[entry.id] = entry
        self._save_entry(entry)
        return entry

    def get(self, entry_id: UUID) -> LabEntry | None:
        """Retrieve an entry by ID."""
        return self._entries.get(entry_id)

    def update(self, entry_id: UUID, **fields: object) -> LabEntry | None:
        """Update fields of an existing entry."""
        entry = self._entries.get(entry_id)
        if entry is None:
            return None
        for key, value in fields.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.now()
        self._save_entry(entry)
        return entry

    def delete(self, entry_id: UUID) -> bool:
        """Delete an entry by ID."""
        if entry_id not in self._entries:
            return False
        del self._entries[entry_id]
        path = self.storage_dir / f"{entry_id}.json"
        if path.exists():
            path.unlink()
        return True

    def list_entries(
        self,
        status: EntryStatus | None = None,
        tags: list[str] | None = None,
    ) -> list[LabEntry]:
        """List entries with optional filtering by status and tags."""
        entries = list(self._entries.values())
        if status is not None:
            entries = [e for e in entries if e.status == status]
        if tags:
            tag_set = set(tags)
            entries = [e for e in entries if tag_set.intersection(e.tags)]
        return sorted(entries, key=lambda e: e.created_at, reverse=True)

    def search_by_title(self, query: str) -> list[LabEntry]:
        """Search entries by title substring (case-insensitive)."""
        q = query.lower()
        return [e for e in self._entries.values() if q in e.title.lower()]

    @property
    def count(self) -> int:
        """Return the total number of entries."""
        return len(self._entries)
