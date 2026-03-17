"""Statistical analysis for experimental data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy import stats


@dataclass
class StatResult:
    """Container for a statistical test result."""

    test_name: str
    statistic: float
    p_value: float
    significant: bool
    effect_size: float | None = None
    details: dict[str, Any] | None = None

    def summary(self) -> str:
        """Return a human-readable summary of the result."""
        sig = "significant" if self.significant else "not significant"
        parts = [
            f"{self.test_name}: statistic={self.statistic:.4f}, p={self.p_value:.4f} ({sig})",
        ]
        if self.effect_size is not None:
            parts.append(f"effect size={self.effect_size:.4f}")
        return ", ".join(parts)


class StatisticalAnalyzer:
    """Computes statistical tests on experimental data.

    Provides t-tests, ANOVA, and correlation analysis with
    sensible defaults and structured result objects.
    """

    def __init__(self, alpha: float = 0.05) -> None:
        self.alpha = alpha

    def t_test(
        self,
        group_a: list[float] | np.ndarray,
        group_b: list[float] | np.ndarray,
        paired: bool = False,
        equal_var: bool = True,
    ) -> StatResult:
        """Perform an independent or paired t-test between two groups.

        Args:
            group_a: First data group.
            group_b: Second data group.
            paired: If True, perform a paired t-test.
            equal_var: Assume equal variances (Welch's t-test if False).

        Returns:
            StatResult with test statistic and p-value.
        """
        a = np.asarray(group_a, dtype=float)
        b = np.asarray(group_b, dtype=float)

        if paired:
            stat, p = stats.ttest_rel(a, b)
            test_name = "Paired t-test"
        else:
            stat, p = stats.ttest_ind(a, b, equal_var=equal_var)
            test_name = "Independent t-test" if equal_var else "Welch's t-test"

        # Cohen's d effect size
        pooled_std = np.sqrt((np.std(a, ddof=1) ** 2 + np.std(b, ddof=1) ** 2) / 2)
        effect_size = float((np.mean(a) - np.mean(b)) / pooled_std) if pooled_std > 0 else 0.0

        return StatResult(
            test_name=test_name,
            statistic=float(stat),
            p_value=float(p),
            significant=float(p) < self.alpha,
            effect_size=effect_size,
            details={
                "mean_a": float(np.mean(a)),
                "mean_b": float(np.mean(b)),
                "std_a": float(np.std(a, ddof=1)),
                "std_b": float(np.std(b, ddof=1)),
                "n_a": len(a),
                "n_b": len(b),
            },
        )

    def anova(self, *groups: list[float] | np.ndarray) -> StatResult:
        """Perform one-way ANOVA across multiple groups.

        Args:
            *groups: Two or more data groups to compare.

        Returns:
            StatResult with F-statistic and p-value.
        """
        if len(groups) < 2:
            raise ValueError("ANOVA requires at least two groups")

        arrays = [np.asarray(g, dtype=float) for g in groups]
        stat, p = stats.f_oneway(*arrays)

        # Eta-squared effect size
        grand_mean = np.mean(np.concatenate(arrays))
        ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in arrays)
        ss_total = sum(np.sum((g - grand_mean) ** 2) for g in arrays)
        eta_sq = float(ss_between / ss_total) if ss_total > 0 else 0.0

        return StatResult(
            test_name="One-way ANOVA",
            statistic=float(stat),
            p_value=float(p),
            significant=float(p) < self.alpha,
            effect_size=eta_sq,
            details={
                "n_groups": len(groups),
                "group_sizes": [len(g) for g in arrays],
                "group_means": [float(np.mean(g)) for g in arrays],
                "eta_squared": eta_sq,
            },
        )

    def correlation(
        self,
        x: list[float] | np.ndarray,
        y: list[float] | np.ndarray,
        method: str = "pearson",
    ) -> StatResult:
        """Compute correlation between two variables.

        Args:
            x: First variable.
            y: Second variable.
            method: One of 'pearson', 'spearman', or 'kendall'.

        Returns:
            StatResult with correlation coefficient and p-value.
        """
        x_arr = np.asarray(x, dtype=float)
        y_arr = np.asarray(y, dtype=float)

        if method == "pearson":
            stat, p = stats.pearsonr(x_arr, y_arr)
        elif method == "spearman":
            stat, p = stats.spearmanr(x_arr, y_arr)
        elif method == "kendall":
            stat, p = stats.kendalltau(x_arr, y_arr)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'pearson', 'spearman', or 'kendall'.")

        return StatResult(
            test_name=f"{method.capitalize()} correlation",
            statistic=float(stat),
            p_value=float(p),
            significant=float(p) < self.alpha,
            effect_size=float(stat),  # r is its own effect size
            details={"method": method, "n": len(x_arr)},
        )

    def descriptive(self, data: list[float] | np.ndarray) -> dict[str, float]:
        """Compute descriptive statistics for a dataset."""
        arr = np.asarray(data, dtype=float)
        return {
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr, ddof=1)),
            "var": float(np.var(arr, ddof=1)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "n": len(arr),
            "sem": float(stats.sem(arr)),
            "skew": float(stats.skew(arr)),
            "kurtosis": float(stats.kurtosis(arr)),
        }
