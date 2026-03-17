"""Tests for the top-level report module."""

import tempfile
from pathlib import Path

from lablog.models import Experiment, LabEntry
from lablog.report import generate_entry_report, generate_experiment_report, generate_summary


class TestReportModule:
    def test_generate_entry_report(self):
        entry = LabEntry(title="Report Test", hypothesis="H1")
        report = generate_entry_report(entry, fmt="markdown", author="Tester")
        assert "Report Test" in report
        assert "Tester" in report

    def test_generate_entry_report_to_file(self):
        entry = LabEntry(title="File Report")
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
            path = f.name
        generate_entry_report(entry, fmt="markdown", output_path=path)
        content = Path(path).read_text()
        assert "File Report" in content

    def test_generate_experiment_report(self):
        exp = Experiment(name="exp-rpt", parameters={"dose": 10})
        report = generate_experiment_report(exp, fmt="markdown")
        assert "exp-rpt" in report
        assert "dose" in report

    def test_generate_summary(self):
        entries = [LabEntry(title="E1")]
        experiments = [Experiment(name="X1")]
        report = generate_summary(entries, experiments, fmt="markdown")
        assert "Summary" in report

    def test_generate_summary_html(self):
        report = generate_summary([], [], fmt="html")
        assert "<html>" in report
