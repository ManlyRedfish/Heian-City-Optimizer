# Heian-City-Optimizer

Heian City Optimizer is a small Python project that demonstrates a greedy hill-climbing
approach to city layout optimization. Provide a scenario that describes the available
building types, their adjacency preferences, and an initial grid and the optimizer will
suggest improvements that respect locked cells.

## Installation

The project is packaged as a standard Python module. Install dependencies and run the
CLI directly:

```bash
python -m pip install -e .
```

## Usage

A sample scenario is available in `scenarios/sample_scenario.json`. Optimize it with:

```bash
python -m heian_city_optimizer.cli optimize scenarios/sample_scenario.json --show-grid
```

The optimizer prints the final score, the number of iterations performed, and (optionally)
an ASCII visualization of the optimized grid. You can also write the optimized grid to a
file by supplying `--output path/to/result.json`.

## Running tests

The repository uses `pytest` for unit testing:

```bash
pytest
```
