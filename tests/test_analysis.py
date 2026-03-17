"""Tests for the analysis module: stats, visualizer, and reporter."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from lablog.analysis.reporter import ReportGenerator
from lablog.analysis.stats import StatisticalAnalyzer
from lablog.analysis.visualizer import ResultVisualizer
from lablog.models import Experiment, LabEntry


class TestStatisticalAnalyzer:
    def setup_method(self):
        self.analyzer = StatisticalAnalyzer(alpha=0.05)

    def test_t_test_independent(self):
        np.random.seed(42)
        a = np.random.normal(10, 2, 30).tolist()
        b = np.random.normal(12, 2, 30).tolist()
        result = self.analyzer.t_test(a, b)
        assert result.test_name == "Independent t-test"
        assert result.p_value < 0.05
        assert result.significant
        assert result.effect_size is not None
        assert "mean_a" in result.details

    def test_t_test_paired(self):
        np.random.seed(42)
        a = np.random.normal(10, 2, 20).tolist()
        b = [x + 0.5 for x in a]
        result = self.analyzer.t_test(a, b, paired=True)
        assert result.test_name == "Paired t-test"

    def test_t_test_welch(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0]
        b = [2.0, 4.0, 6.0, 8.0, 10.0]
        result = self.analyzer.t_test(a, b, equal_var=False)
        assert result.test_name == "Welch's t-test"

    def test_anova(self):
        np.random.seed(42)
        g1 = np.random.normal(10, 1, 20).tolist()
        g2 = np.random.normal(12, 1, 20).tolist()
        g3 = np.random.normal(14, 1, 20).tolist()
        result = self.analyzer.anova(g1, g2, g3)
        assert result.test_name == "One-way ANOVA"
        assert result.significant
        assert result.details["n_groups"] == 3
        assert result.effect_size > 0

    def test_anova_requires_two_groups(self):
        with pytest.raises(ValueError, match="at least two"):
            self.analyzer.anova([1, 2, 3])

    def test_correlation_pearson(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2, 4, 5, 8, 9, 12, 14, 15, 18, 20]
        result = self.analyzer.correlation(x, y)
        assert result.test_name == "Pearson correlation"
        assert result.statistic > 0.95
        assert result.significant

    def test_correlation_spearman(self):
        x = [1, 2, 3, 4, 5]
        y = [5, 4, 3, 2, 1]
        result = self.analyzer.correlation(x, y, method="spearman")
        assert result.statistic < -0.9

    def test_correlation_kendall(self):
        x = [1, 2, 3, 4, 5]
        y = [1, 3, 2, 5, 4]
        result = self.analyzer.correlation(x, y, method="kendall")
        assert result.test_name == "Kendall correlation"

    def test_correlation_invalid_method(self):
        with pytest.raises(ValueError, match="Unknown method"):
            self.analyzer.correlation([1], [2], method="invalid")

    def test_descriptive(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        desc = self.analyzer.descriptive(data)
        assert desc["mean"] == 5.5
        assert desc["n"] == 10
        assert desc["min"] == 1.0
        assert desc["max"] == 10.0
        assert "std" in desc
        assert "sem" in desc

    def test_stat_result_summary(self):
        result = self.analyzer.t_test([1, 2, 3], [4, 5, 6])
        summary = result.summary()
        assert "t-test" in summary
        assert "p=" in summary


class TestResultVisualizer:
    def setup_method(self):
        self.viz = ResultVisualizer()

    def teardown_method(self):
        self.viz.close_all()

    def test_plot_comparison(self):
        data = {"Control": [1, 2, 3, 4], "Treatment": [3, 4, 5, 6]}
        fig = self.viz.plot_comparison(data, title="Test Comparison")
        assert fig is not None

    def test_plot_comparison_save(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            data = {"A": [1, 2], "B": [3, 4]}
            self.viz.plot_comparison(data, output_path=f.name)
            assert Path(f.name).stat().st_size > 0

    def test_plot_bar_chart(self):
        fig = self.viz.plot_bar_chart(
            labels=["A", "B", "C"],
            values=[10, 20, 15],
            errors=[1, 2, 1.5],
        )
        assert fig is not None

    def test_plot_scatter(self):
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 5, 4, 6]
        fig = self.viz.plot_scatter(x, y, trend_line=True)
        assert fig is not None

    def test_plot_metrics_over_time(self):
        exp = Experiment(name="viz-test")
        exp.log_metric("loss", 0.9)
        exp.log_metric("loss", 0.5)
        exp.log_metric("loss", 0.2)
        fig = self.viz.plot_metrics_over_time(exp, "loss")
        assert fig is not None

    def test_plot_metrics_no_data(self):
        exp = Experiment(name="empty")
        with pytest.raises(ValueError, match="No metrics"):
            self.viz.plot_metrics_over_time(exp, "missing")


class TestReportGenerator:
    def setup_method(self):
        self.gen = ReportGenerator(author="Test Author")

    def test_entry_markdown(self):
        entry = LabEntry(
            title="Test Entry",
            hypothesis="H1",
            procedure="P1",
            observations="O1",
            results="R1",
            conclusions="C1",
            tags=["bio"],
        )
        report = self.gen.generate_entry_report(entry, fmt="markdown")
        assert "# Test Entry" in report
        assert "## Hypothesis" in report
        assert "Test Author" in report
        assert "bio" in report

    def test_entry_html(self):
        entry = LabEntry(title="HTML Test", hypothesis="H")
        report = self.gen.generate_entry_report(entry, fmt="html")
        assert "<h1>HTML Test</h1>" in report
        assert "<h2>Hypothesis</h2>" in report

    def test_entry_json(self):
        entry = LabEntry(title="JSON Test")
        report = self.gen.generate_entry_report(entry, fmt="json")
        assert '"title": "JSON Test"' in report

    def test_experiment_markdown(self):
        exp = Experiment(name="exp-rpt", parameters={"temp": 37})
        exp.log_metric("yield", 85.5, unit="%")
        report = self.gen.generate_experiment_report(exp, fmt="markdown")
        assert "# Experiment: exp-rpt" in report
        assert "temp" in report
        assert "85.5" in report

    def test_summary_report(self):
        entries = [LabEntry(title="E1"), LabEntry(title="E2")]
        experiments = [Experiment(name="X1")]
        report = self.gen.generate_summary_report(entries, experiments)
        assert "Summary" in report
        assert "Total entries:** 2" in report

    def test_invalid_format(self):
        entry = LabEntry(title="Bad")
        with pytest.raises(ValueError):
            self.gen.generate_entry_report(entry, fmt="pdf")
