"""Tests for the CLI interface."""

import tempfile

from click.testing import CliRunner

from lablog.cli import cli


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_version(self):
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_entry_create(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                "entry", "create", "--title", "CLI Test Entry",
                "--hypothesis", "Test hypothesis",
            ])
            assert result.exit_code == 0
            assert "Entry created" in result.output

    def test_entry_list_empty(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["entry", "list"])
            assert result.exit_code == 0

    def test_experiment_create(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                "experiment", "create", "--name", "CLI Experiment",
            ])
            assert result.exit_code == 0
            assert "Experiment created" in result.output

    def test_experiment_list_empty(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["experiment", "list"])
            assert result.exit_code == 0

    def test_search_empty(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["search", "test"])
            assert result.exit_code == 0

    def test_report_generate(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["report", "generate"])
            assert result.exit_code == 0
