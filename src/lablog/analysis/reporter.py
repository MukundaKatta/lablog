"""Report generation for formatted lab reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from lablog.models import Experiment, LabEntry, Protocol


class ReportGenerator:
    """Creates formatted lab reports in Markdown, HTML, or JSON."""

    def __init__(self, author: str = "") -> None:
        self.author = author

    def generate_entry_report(self, entry: LabEntry, fmt: str = "markdown") -> str:
        """Generate a formatted report for a single lab entry.

        Args:
            entry: The lab entry to report on.
            fmt: Output format - 'markdown', 'html', or 'json'.

        Returns:
            Formatted report string.
        """
        if fmt == "markdown":
            return self._entry_markdown(entry)
        elif fmt == "html":
            return self._entry_html(entry)
        elif fmt == "json":
            return entry.model_dump_json(indent=2)
        else:
            raise ValueError(f"Unknown format: {fmt}")

    def generate_experiment_report(self, experiment: Experiment, fmt: str = "markdown") -> str:
        """Generate a formatted report for an experiment.

        Args:
            experiment: The experiment to report on.
            fmt: Output format - 'markdown', 'html', or 'json'.

        Returns:
            Formatted report string.
        """
        if fmt == "markdown":
            return self._experiment_markdown(experiment)
        elif fmt == "html":
            return self._experiment_html(experiment)
        elif fmt == "json":
            return experiment.model_dump_json(indent=2)
        else:
            raise ValueError(f"Unknown format: {fmt}")

    def generate_summary_report(
        self,
        entries: list[LabEntry],
        experiments: list[Experiment],
        fmt: str = "markdown",
    ) -> str:
        """Generate a summary report across multiple entries and experiments.

        Args:
            entries: List of lab entries.
            experiments: List of experiments.
            fmt: Output format.

        Returns:
            Formatted summary report string.
        """
        if fmt == "markdown":
            return self._summary_markdown(entries, experiments)
        elif fmt == "html":
            return self._summary_html(entries, experiments)
        else:
            raise ValueError(f"Unknown format for summary: {fmt}")

    # -- Markdown formatters --

    def _entry_markdown(self, entry: LabEntry) -> str:
        sections = [
            f"# {entry.title}",
            f"**Date:** {entry.created_at:%Y-%m-%d %H:%M}",
            f"**Status:** {entry.status.value}",
        ]
        if self.author:
            sections.append(f"**Author:** {self.author}")
        if entry.tags:
            sections.append(f"**Tags:** {', '.join(entry.tags)}")
        sections.append("")
        if entry.hypothesis:
            sections.extend(["## Hypothesis", entry.hypothesis, ""])
        if entry.procedure:
            sections.extend(["## Procedure", entry.procedure, ""])
        if entry.observations:
            sections.extend(["## Observations", entry.observations, ""])
        if entry.results:
            sections.extend(["## Results", entry.results, ""])
        if entry.conclusions:
            sections.extend(["## Conclusions", entry.conclusions, ""])
        return "\n".join(sections)

    def _experiment_markdown(self, exp: Experiment) -> str:
        sections = [
            f"# Experiment: {exp.name}",
            f"**Status:** {exp.status.value}",
            f"**Created:** {exp.created_at:%Y-%m-%d %H:%M}",
        ]
        if exp.description:
            sections.extend(["", exp.description])
        if exp.parameters:
            sections.extend(["", "## Parameters", ""])
            for k, v in exp.parameters.items():
                sections.append(f"- **{k}:** {v}")
        if exp.metrics:
            sections.extend(["", "## Metrics", ""])
            sections.append("| Metric | Value | Unit | Time |")
            sections.append("|--------|-------|------|------|")
            for m in exp.metrics:
                sections.append(f"| {m.name} | {m.value} | {m.unit} | {m.timestamp:%H:%M:%S} |")
        if exp.artifacts:
            sections.extend(["", "## Artifacts", ""])
            for a in exp.artifacts:
                sections.append(f"- **{a.name}** ({a.artifact_type}): `{a.path}`")
                if a.description:
                    sections.append(f"  {a.description}")
        return "\n".join(sections)

    def _summary_markdown(self, entries: list[LabEntry], experiments: list[Experiment]) -> str:
        now = datetime.now()
        sections = [
            f"# Lab Notebook Summary",
            f"**Generated:** {now:%Y-%m-%d %H:%M}",
        ]
        if self.author:
            sections.append(f"**Author:** {self.author}")
        sections.extend([
            "",
            f"## Overview",
            f"- **Total entries:** {len(entries)}",
            f"- **Total experiments:** {len(experiments)}",
            "",
        ])
        if entries:
            sections.append("## Recent Entries\n")
            for entry in entries[:10]:
                sections.append(f"- [{entry.status.value}] **{entry.title}** ({entry.created_at:%Y-%m-%d})")
        if experiments:
            sections.append("\n## Recent Experiments\n")
            for exp in experiments[:10]:
                sections.append(
                    f"- [{exp.status.value}] **{exp.name}** - {len(exp.metrics)} metrics"
                )
        return "\n".join(sections)

    # -- HTML formatters --

    def _entry_html(self, entry: LabEntry) -> str:
        parts = [
            "<html><body>",
            f"<h1>{entry.title}</h1>",
            f"<p><strong>Date:</strong> {entry.created_at:%Y-%m-%d %H:%M}</p>",
            f"<p><strong>Status:</strong> {entry.status.value}</p>",
        ]
        if entry.tags:
            parts.append(f"<p><strong>Tags:</strong> {', '.join(entry.tags)}</p>")
        for field, label in [
            ("hypothesis", "Hypothesis"),
            ("procedure", "Procedure"),
            ("observations", "Observations"),
            ("results", "Results"),
            ("conclusions", "Conclusions"),
        ]:
            value = getattr(entry, field)
            if value:
                parts.extend([f"<h2>{label}</h2>", f"<p>{value}</p>"])
        parts.append("</body></html>")
        return "\n".join(parts)

    def _experiment_html(self, exp: Experiment) -> str:
        parts = [
            "<html><body>",
            f"<h1>Experiment: {exp.name}</h1>",
            f"<p><strong>Status:</strong> {exp.status.value}</p>",
        ]
        if exp.parameters:
            parts.append("<h2>Parameters</h2><ul>")
            for k, v in exp.parameters.items():
                parts.append(f"<li><strong>{k}:</strong> {v}</li>")
            parts.append("</ul>")
        if exp.metrics:
            parts.append("<h2>Metrics</h2><table><tr><th>Metric</th><th>Value</th><th>Unit</th></tr>")
            for m in exp.metrics:
                parts.append(f"<tr><td>{m.name}</td><td>{m.value}</td><td>{m.unit}</td></tr>")
            parts.append("</table>")
        parts.append("</body></html>")
        return "\n".join(parts)

    def _summary_html(self, entries: list[LabEntry], experiments: list[Experiment]) -> str:
        parts = [
            "<html><body>",
            "<h1>Lab Notebook Summary</h1>",
            f"<p>Entries: {len(entries)}, Experiments: {len(experiments)}</p>",
        ]
        if entries:
            parts.append("<h2>Entries</h2><ul>")
            for e in entries[:10]:
                parts.append(f"<li>[{e.status.value}] {e.title}</li>")
            parts.append("</ul>")
        if experiments:
            parts.append("<h2>Experiments</h2><ul>")
            for ex in experiments[:10]:
                parts.append(f"<li>[{ex.status.value}] {ex.name}</li>")
            parts.append("</ul>")
        parts.append("</body></html>")
        return "\n".join(parts)
