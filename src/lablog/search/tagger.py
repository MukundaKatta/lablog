"""Automatic keyword and entity extraction from lab entries."""

from __future__ import annotations

import re
from collections import Counter

from lablog.models import LabEntry


# Common scientific method terms
_METHOD_PATTERNS: list[str] = [
    r"\bpcr\b",
    r"\bwestern\s*blot\b",
    r"\belisa\b",
    r"\bflow\s*cytometry\b",
    r"\bmass\s*spec(?:trometry)?\b",
    r"\bchip[-\s]?seq\b",
    r"\brna[-\s]?seq\b",
    r"\bmicroscopy\b",
    r"\bcentrifug(?:ation|e)\b",
    r"\belectrophoresis\b",
    r"\bchromatography\b",
    r"\bspectrophotometry\b",
    r"\bincubat(?:ion|e|ed)\b",
    r"\btransfect(?:ion|ed)\b",
    r"\bsequencing\b",
    r"\bcloning\b",
    r"\bcultur(?:e|ed|ing)\b",
    r"\bassay\b",
    r"\btitrat(?:ion|e)\b",
    r"\bdilut(?:ion|e|ed)\b",
]

# Common reagent / chemical patterns
_REAGENT_PATTERNS: list[str] = [
    r"\bdmso\b",
    r"\bpbs\b",
    r"\bedta\b",
    r"\btris\b",
    r"\bsds\b",
    r"\bethanol\b",
    r"\bmethanol\b",
    r"\bformaldehyde\b",
    r"\bantibod(?:y|ies)\b",
    r"\bprimer[s]?\b",
    r"\bplasmid[s]?\b",
    r"\bbuffer\b",
    r"\bmedium\b",
    r"\bserum\b",
    r"\bagar(?:ose)?\b",
    r"\bprotease\b",
    r"\binhibitor\b",
    r"\bsubstrate\b",
    r"\bligand\b",
    r"\benzyme\b",
]

# Stop words to exclude from keywords
_STOP_WORDS: set[str] = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "was", "were", "is", "are", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "this", "that",
    "these", "those", "it", "its", "not", "no", "we", "our", "us",
    "then", "than", "each", "per", "into", "also", "after", "before",
    "between", "through", "during", "under", "over", "about", "such",
    "very", "more", "most", "all", "any", "both", "some", "other",
    "using", "used", "sample", "samples", "data", "result", "results",
}


class AutoTagger:
    """Extracts keywords, methods, and reagents from lab entries.

    Uses pattern matching for known scientific methods and reagents,
    and frequency-based extraction for general keywords.
    """

    def __init__(
        self,
        extra_method_patterns: list[str] | None = None,
        extra_reagent_patterns: list[str] | None = None,
    ) -> None:
        self._method_patterns = _METHOD_PATTERNS.copy()
        if extra_method_patterns:
            self._method_patterns.extend(extra_method_patterns)
        self._reagent_patterns = _REAGENT_PATTERNS.copy()
        if extra_reagent_patterns:
            self._reagent_patterns.extend(extra_reagent_patterns)

    def _get_text(self, entry: LabEntry) -> str:
        """Concatenate searchable text from an entry."""
        return " ".join([
            entry.title,
            entry.hypothesis,
            entry.procedure,
            entry.observations,
            entry.results,
            entry.conclusions,
        ])

    def extract_methods(self, entry: LabEntry) -> list[str]:
        """Extract scientific methods mentioned in the entry."""
        text = self._get_text(entry).lower()
        methods = []
        for pattern in self._method_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                methods.append(match.group(0).strip())
        return sorted(set(methods))

    def extract_reagents(self, entry: LabEntry) -> list[str]:
        """Extract reagents and chemicals mentioned in the entry."""
        text = self._get_text(entry).lower()
        reagents = []
        for pattern in self._reagent_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                reagents.append(match.group(0).strip())
        return sorted(set(reagents))

    def extract_keywords(self, entry: LabEntry, top_n: int = 10) -> list[str]:
        """Extract top keywords by frequency, excluding stop words.

        Args:
            entry: The lab entry to process.
            top_n: Number of keywords to return.

        Returns:
            List of keywords sorted by frequency.
        """
        text = self._get_text(entry).lower()
        words = re.findall(r"[a-z]{3,}", text)
        filtered = [w for w in words if w not in _STOP_WORDS]
        counts = Counter(filtered)
        return [word for word, _ in counts.most_common(top_n)]

    def auto_tag(self, entry: LabEntry, max_tags: int = 15) -> list[str]:
        """Generate a combined set of tags for an entry.

        Merges methods, reagents, and top keywords into a single tag list.

        Args:
            entry: The lab entry to tag.
            max_tags: Maximum number of tags to return.

        Returns:
            List of suggested tags.
        """
        tags: list[str] = []
        tags.extend(self.extract_methods(entry))
        tags.extend(self.extract_reagents(entry))
        keywords = self.extract_keywords(entry)
        for kw in keywords:
            if kw not in tags:
                tags.append(kw)
            if len(tags) >= max_tags:
                break
        return tags[:max_tags]
