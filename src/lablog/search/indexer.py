"""Full-text search indexing across lab entries."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from uuid import UUID

from lablog.models import LabEntry


class EntryIndexer:
    """Provides full-text search across lab notebook entries.

    Builds an inverted index over entry fields and supports ranked
    retrieval using TF-IDF scoring.
    """

    def __init__(self) -> None:
        # token -> {entry_id -> count}
        self._index: dict[str, dict[UUID, int]] = defaultdict(dict)
        self._entries: dict[UUID, LabEntry] = {}
        self._doc_count = 0

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Split text into lowercase tokens."""
        return re.findall(r"[a-z0-9]+", text.lower())

    def _extract_text(self, entry: LabEntry) -> str:
        """Concatenate all searchable fields from an entry."""
        return " ".join([
            entry.title,
            entry.hypothesis,
            entry.procedure,
            entry.observations,
            entry.results,
            entry.conclusions,
            " ".join(entry.tags),
        ])

    def add_entry(self, entry: LabEntry) -> None:
        """Index a lab entry for search."""
        self._entries[entry.id] = entry
        text = self._extract_text(entry)
        tokens = self._tokenize(text)
        token_counts: dict[str, int] = defaultdict(int)
        for token in tokens:
            token_counts[token] += 1
        for token, count in token_counts.items():
            self._index[token][entry.id] = count
        self._doc_count = len(self._entries)

    def remove_entry(self, entry_id: UUID) -> None:
        """Remove an entry from the index."""
        if entry_id not in self._entries:
            return
        del self._entries[entry_id]
        empty_tokens = []
        for token, postings in self._index.items():
            postings.pop(entry_id, None)
            if not postings:
                empty_tokens.append(token)
        for token in empty_tokens:
            del self._index[token]
        self._doc_count = len(self._entries)

    def reindex(self, entries: list[LabEntry]) -> None:
        """Rebuild the full index from a list of entries."""
        self._index = defaultdict(dict)
        self._entries = {}
        self._doc_count = 0
        for entry in entries:
            self.add_entry(entry)

    def search(self, query: str, limit: int = 20) -> list[tuple[LabEntry, float]]:
        """Search entries by query string, ranked by TF-IDF score.

        Args:
            query: Search query string.
            limit: Maximum number of results.

        Returns:
            List of (entry, score) tuples sorted by relevance.
        """
        tokens = self._tokenize(query)
        if not tokens:
            return []

        scores: dict[UUID, float] = defaultdict(float)
        for token in tokens:
            postings = self._index.get(token, {})
            if not postings:
                continue
            idf = math.log(1 + self._doc_count / len(postings))
            for entry_id, tf in postings.items():
                scores[entry_id] += tf * idf

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        return [(self._entries[eid], score) for eid, score in ranked if eid in self._entries]

    @property
    def indexed_count(self) -> int:
        """Return the number of indexed entries."""
        return self._doc_count

    @property
    def vocabulary_size(self) -> int:
        """Return the number of unique tokens in the index."""
        return len(self._index)
