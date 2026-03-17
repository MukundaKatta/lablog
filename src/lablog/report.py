"""High-level report generation utilities."""

from __future__ import annotations

from pathlib import Path

from lablog.analysis.reporter import ReportGenerator
from lablog.models import Experiment, LabEntry


def generate_entry_report(
    entry: LabEntry,
    fmt: str = "markdown",
    output_path: str | Path | None = None,
    author: str = "",
) -> str:
    """Generate a formatted report for a lab entry and optionally save to file.

    Args:
        entry: The lab entry to generate a report for.
        fmt: Output format ('markdown', 'html', or 'json').
        output_path: Optional file path to write the report.
        author: Author name to include in the report.

    Returns:
        The formatted report as a string.
    """
    generator = ReportGenerator(author=author)
    report = generator.generate_entry_report(entry, fmt=fmt)
    if output_path:
        Path(output_path).write_text(report)
    return report


def generate_experiment_report(
    experiment: Experiment,
    fmt: str = "markdown",
    output_path: str | Path | None = None,
    author: str = "",
) -> str:
    """Generate a formatted report for an experiment and optionally save to file.

    Args:
        experiment: The experiment to generate a report for.
        fmt: Output format ('markdown', 'html', or 'json').
        output_path: Optional file path to write the report.
        author: Author name to include in the report.

    Returns:
        The formatted report as a string.
    """
    generator = ReportGenerator(author=author)
    report = generator.generate_experiment_report(experiment, fmt=fmt)
    if output_path:
        Path(output_path).write_text(report)
    return report


def generate_summary(
    entries: list[LabEntry],
    experiments: list[Experiment],
    fmt: str = "markdown",
    output_path: str | Path | None = None,
    author: str = "",
) -> str:
    """Generate a summary report across entries and experiments.

    Args:
        entries: List of lab entries to summarize.
        experiments: List of experiments to summarize.
        fmt: Output format ('markdown' or 'html').
        output_path: Optional file path to write the report.
        author: Author name to include in the report.

    Returns:
        The formatted summary as a string.
    """
    generator = ReportGenerator(author=author)
    report = generator.generate_summary_report(entries, experiments, fmt=fmt)
    if output_path:
        Path(output_path).write_text(report)
    return report
