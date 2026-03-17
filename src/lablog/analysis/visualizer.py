"""Result visualization using matplotlib."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from lablog.models import Experiment


class ResultVisualizer:
    """Plots experiment results using matplotlib."""

    def __init__(self, style: str = "seaborn-v0_8-whitegrid", figsize: tuple[int, int] = (10, 6)) -> None:
        self.figsize = figsize
        try:
            plt.style.use(style)
        except OSError:
            pass  # Fall back to default style

    def plot_metrics_over_time(
        self,
        experiment: Experiment,
        metric_name: str,
        output_path: str | Path | None = None,
        title: str | None = None,
    ) -> plt.Figure:
        """Plot a metric's values over time for an experiment.

        Args:
            experiment: The experiment to plot.
            metric_name: Name of the metric to plot.
            output_path: Optional path to save the figure.
            title: Optional custom title.

        Returns:
            The matplotlib Figure.
        """
        metrics = [m for m in experiment.metrics if m.name == metric_name]
        if not metrics:
            raise ValueError(f"No metrics found with name '{metric_name}'")

        timestamps = [m.timestamp for m in metrics]
        values = [m.value for m in metrics]

        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(timestamps, values, marker="o", linewidth=2)
        ax.set_xlabel("Time")
        ax.set_ylabel(f"{metric_name}" + (f" ({metrics[0].unit})" if metrics[0].unit else ""))
        ax.set_title(title or f"{experiment.name}: {metric_name} over time")
        fig.autofmt_xdate()
        fig.tight_layout()

        if output_path:
            fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
        return fig

    def plot_comparison(
        self,
        data: dict[str, list[float]],
        output_path: str | Path | None = None,
        title: str = "Experiment Comparison",
        ylabel: str = "Value",
    ) -> plt.Figure:
        """Create a box plot comparing data across named groups.

        Args:
            data: Mapping from group name to list of values.
            output_path: Optional path to save the figure.
            title: Plot title.
            ylabel: Y-axis label.

        Returns:
            The matplotlib Figure.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        labels = list(data.keys())
        values = list(data.values())

        ax.boxplot(values, labels=labels)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        fig.tight_layout()

        if output_path:
            fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
        return fig

    def plot_bar_chart(
        self,
        labels: list[str],
        values: list[float],
        errors: list[float] | None = None,
        output_path: str | Path | None = None,
        title: str = "Results",
        ylabel: str = "Value",
    ) -> plt.Figure:
        """Create a bar chart with optional error bars.

        Args:
            labels: Category labels.
            values: Bar heights.
            errors: Optional error bar values.
            output_path: Optional path to save the figure.
            title: Plot title.
            ylabel: Y-axis label.

        Returns:
            The matplotlib Figure.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        x = np.arange(len(labels))
        ax.bar(x, values, yerr=errors, capsize=5, color="steelblue", alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        fig.tight_layout()

        if output_path:
            fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
        return fig

    def plot_scatter(
        self,
        x: list[float] | np.ndarray,
        y: list[float] | np.ndarray,
        output_path: str | Path | None = None,
        title: str = "Scatter Plot",
        xlabel: str = "X",
        ylabel: str = "Y",
        trend_line: bool = False,
    ) -> plt.Figure:
        """Create a scatter plot with optional trend line.

        Args:
            x: X-axis values.
            y: Y-axis values.
            output_path: Optional path to save the figure.
            title: Plot title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            trend_line: Whether to add a linear trend line.

        Returns:
            The matplotlib Figure.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        ax.scatter(x, y, alpha=0.7, edgecolors="black", linewidths=0.5)

        if trend_line:
            x_arr = np.asarray(x, dtype=float)
            y_arr = np.asarray(y, dtype=float)
            z = np.polyfit(x_arr, y_arr, 1)
            p = np.poly1d(z)
            x_line = np.linspace(x_arr.min(), x_arr.max(), 100)
            ax.plot(x_line, p(x_line), "r--", linewidth=1.5, label=f"y={z[0]:.2f}x+{z[1]:.2f}")
            ax.legend()

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        fig.tight_layout()

        if output_path:
            fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
        return fig

    @staticmethod
    def close_all() -> None:
        """Close all open matplotlib figures to free memory."""
        plt.close("all")
