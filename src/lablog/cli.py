"""Command-line interface for LABLOG using Click and Rich."""

from __future__ import annotations

from uuid import UUID

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lablog.analysis.reporter import ReportGenerator
from lablog.models import EntryStatus, ExperimentStatus
from lablog.notebook.entry import LabEntryManager
from lablog.notebook.experiment import ExperimentTracker
from lablog.search.indexer import EntryIndexer
from lablog.search.tagger import AutoTagger

console = Console()

# Shared state: lazily-initialized managers
_entry_mgr: LabEntryManager | None = None
_exp_tracker: ExperimentTracker | None = None


def _get_entry_manager() -> LabEntryManager:
    global _entry_mgr
    if _entry_mgr is None:
        _entry_mgr = LabEntryManager()
    return _entry_mgr


def _get_experiment_tracker() -> ExperimentTracker:
    global _exp_tracker
    if _exp_tracker is None:
        _exp_tracker = ExperimentTracker()
    return _exp_tracker


@click.group()
@click.version_option(package_name="lablog")
def cli() -> None:
    """LABLOG - AI Lab Notebook for experiment tracking and analysis."""


# -- Entry commands --


@cli.group()
def entry() -> None:
    """Manage lab notebook entries."""


@entry.command("create")
@click.option("--title", "-t", required=True, help="Entry title")
@click.option("--hypothesis", "-h", default="", help="Hypothesis")
@click.option("--procedure", "-p", default="", help="Procedure")
@click.option("--observations", "-o", default="", help="Observations")
@click.option("--results", "-r", default="", help="Results")
@click.option("--conclusions", "-c", default="", help="Conclusions")
@click.option("--tag", multiple=True, help="Tags (can be repeated)")
def entry_create(
    title: str,
    hypothesis: str,
    procedure: str,
    observations: str,
    results: str,
    conclusions: str,
    tag: tuple[str, ...],
) -> None:
    """Create a new lab notebook entry."""
    mgr = _get_entry_manager()
    e = mgr.create(
        title=title,
        hypothesis=hypothesis,
        procedure=procedure,
        observations=observations,
        results=results,
        conclusions=conclusions,
        tags=list(tag),
    )
    console.print(Panel(f"[green]Entry created:[/green] {e.title}\nID: {e.id}"))


@entry.command("list")
@click.option("--status", type=click.Choice([s.value for s in EntryStatus]), default=None)
def entry_list(status: str | None) -> None:
    """List all lab entries."""
    mgr = _get_entry_manager()
    es = EntryStatus(status) if status else None
    entries = mgr.list_entries(status=es)
    if not entries:
        console.print("[yellow]No entries found.[/yellow]")
        return
    table = Table(title="Lab Entries")
    table.add_column("ID", style="dim", max_width=12)
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Tags")
    table.add_column("Created")
    for e in entries:
        table.add_row(
            str(e.id)[:8],
            e.title,
            e.status.value,
            ", ".join(e.tags),
            f"{e.created_at:%Y-%m-%d}",
        )
    console.print(table)


@entry.command("show")
@click.argument("entry_id")
def entry_show(entry_id: str) -> None:
    """Show details of a specific entry."""
    mgr = _get_entry_manager()
    e = mgr.get(UUID(entry_id))
    if e is None:
        console.print(f"[red]Entry not found: {entry_id}[/red]")
        return
    gen = ReportGenerator()
    console.print(gen.generate_entry_report(e, fmt="markdown"))


# -- Experiment commands --


@cli.group()
def experiment() -> None:
    """Manage experiments."""


@experiment.command("create")
@click.option("--name", "-n", required=True, help="Experiment name")
@click.option("--description", "-d", default="", help="Description")
@click.option("--tag", multiple=True, help="Tags")
def experiment_create(name: str, description: str, tag: tuple[str, ...]) -> None:
    """Create a new experiment."""
    tracker = _get_experiment_tracker()
    exp = tracker.create(name=name, description=description, tags=list(tag))
    console.print(Panel(f"[green]Experiment created:[/green] {exp.name}\nID: {exp.id}"))


@experiment.command("list")
@click.option("--status", type=click.Choice([s.value for s in ExperimentStatus]), default=None)
def experiment_list(status: str | None) -> None:
    """List all experiments."""
    tracker = _get_experiment_tracker()
    es = ExperimentStatus(status) if status else None
    experiments = tracker.list_experiments(status=es)
    if not experiments:
        console.print("[yellow]No experiments found.[/yellow]")
        return
    table = Table(title="Experiments")
    table.add_column("ID", style="dim", max_width=12)
    table.add_column("Name", style="bold")
    table.add_column("Status")
    table.add_column("Metrics")
    table.add_column("Created")
    for exp in experiments:
        table.add_row(
            str(exp.id)[:8],
            exp.name,
            exp.status.value,
            str(len(exp.metrics)),
            f"{exp.created_at:%Y-%m-%d}",
        )
    console.print(table)


# -- Search commands --


@cli.command("search")
@click.argument("query")
@click.option("--limit", "-l", default=10, help="Maximum results")
def search(query: str, limit: int) -> None:
    """Search across all lab entries."""
    mgr = _get_entry_manager()
    indexer = EntryIndexer()
    for e in mgr.list_entries():
        indexer.add_entry(e)
    results = indexer.search(query, limit=limit)
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
    table = Table(title=f"Search results for '{query}'")
    table.add_column("Score", justify="right")
    table.add_column("Title", style="bold")
    table.add_column("Status")
    table.add_column("Tags")
    for e, score in results:
        table.add_row(f"{score:.2f}", e.title, e.status.value, ", ".join(e.tags))
    console.print(table)


# -- Report commands --


@cli.group()
def report() -> None:
    """Generate reports."""


@report.command("generate")
@click.option("--format", "fmt", type=click.Choice(["markdown", "html"]), default="markdown")
@click.option("--output", "-o", default=None, help="Output file path")
@click.option("--author", default="", help="Author name")
def report_generate(fmt: str, output: str | None, author: str) -> None:
    """Generate a summary report of all entries and experiments."""
    mgr = _get_entry_manager()
    tracker = _get_experiment_tracker()
    gen = ReportGenerator(author=author)
    report_text = gen.generate_summary_report(
        mgr.list_entries(), tracker.list_experiments(), fmt=fmt
    )
    if output:
        from pathlib import Path

        Path(output).write_text(report_text)
        console.print(f"[green]Report saved to {output}[/green]")
    else:
        console.print(report_text)


# -- Tag commands --


@cli.command("auto-tag")
@click.argument("entry_id")
def auto_tag(entry_id: str) -> None:
    """Automatically generate tags for an entry."""
    mgr = _get_entry_manager()
    e = mgr.get(UUID(entry_id))
    if e is None:
        console.print(f"[red]Entry not found: {entry_id}[/red]")
        return
    tagger = AutoTagger()
    tags = tagger.auto_tag(e)
    console.print(f"[bold]Suggested tags:[/bold] {', '.join(tags)}")


if __name__ == "__main__":
    cli()
