# LABLOG - AI Lab Notebook

A structured digital lab notebook for scientific experiment tracking, analysis, and reporting.

## Features

- **Structured Entries**: Record hypotheses, procedures, observations, results, and conclusions
- **Experiment Tracking**: Track parameters, metrics, and artifacts for each experiment
- **Protocol Templates**: Define reproducible experiment procedures
- **Statistical Analysis**: Compute t-tests, ANOVA, and correlations from experimental data
- **Visualization**: Plot experiment results with matplotlib
- **Report Generation**: Create formatted lab reports in Markdown, HTML, or JSON
- **Full-Text Search**: Index and search across all notebook entries
- **Auto-Tagging**: Automatically extract keywords, methods, and reagents from entries

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from lablog.models import LabEntry, Experiment, Protocol
from lablog.notebook.entry import LabEntryManager
from lablog.notebook.experiment import ExperimentTracker
from lablog.analysis.stats import StatisticalAnalyzer

# Create a lab entry
entry = LabEntry(
    title="Cell Growth Assay",
    hypothesis="Compound X inhibits cell growth at 10uM",
    procedure="1. Plate cells\n2. Add compound\n3. Measure viability",
    observations="Reduced confluence observed at 24h",
    results="IC50 = 8.3uM",
    conclusions="Hypothesis supported - compound effective below 10uM",
    tags=["cell-growth", "compound-x"],
)

# Track an experiment
experiment = Experiment(
    name="dose-response-001",
    parameters={"compound": "X", "concentrations": [1, 5, 10, 50]},
)

# Run statistical analysis
analyzer = StatisticalAnalyzer()
result = analyzer.t_test(control_data, treatment_data)
```

## CLI Usage

```bash
# Create a new entry
lablog entry create --title "My Experiment"

# List entries
lablog entry list

# Search entries
lablog search "cell growth"

# Generate a report
lablog report generate --format markdown
```

## Project Structure

```
src/lablog/
  cli.py            - Command-line interface (Click + Rich)
  models.py         - Pydantic data models
  report.py         - Report generation utilities
  notebook/
    entry.py        - Lab entry management
    experiment.py   - Experiment tracking
    protocol.py     - Protocol templates
  analysis/
    stats.py        - Statistical analysis
    visualizer.py   - Result visualization
    reporter.py     - Formatted report generation
  search/
    indexer.py      - Full-text search indexing
    tagger.py       - Automatic keyword extraction
```

## License

MIT
