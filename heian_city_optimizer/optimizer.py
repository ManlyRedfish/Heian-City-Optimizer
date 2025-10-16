"""Optimization routines for the Heian City Optimizer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import CityGrid, CityScenario
from .scoring import CityScorer


@dataclass
class OptimizationResult:
    """Result of an optimization run."""

    grid: CityGrid
    score: float
    iterations: int

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "iterations": self.iterations,
            "grid": self.grid.to_serializable(),
        }

    def render_ascii(self) -> str:
        rows = [
            " ".join(cell if cell is not None else "--" for cell in row)
            for row in self.grid.to_matrix()
        ]
        return "\n".join(rows)


class CityOptimizer:
    """Greedy hill-climbing optimizer for the city layout."""

    def __init__(self, scenario: CityScenario) -> None:
        self.scenario = scenario
        self.scorer = CityScorer(scenario)

    def optimize(self, max_iterations: int = 200) -> OptimizationResult:
        grid = self.scenario.grid.copy()
        score = self.scorer.total_score(grid)
        for iteration in range(1, max_iterations + 1):
            best_delta = 0.0
            best_assignment: Optional[tuple[int, int, Optional[str]]] = None
            for row, col in grid.iter_coords():
                if self.scenario.is_locked((row, col)):
                    continue
                current_value = grid.get(row, col)
                # Try clearing the cell
                delta = self.scorer.delta_for_assignment(grid, row, col, None)
                if delta > best_delta:
                    best_delta = delta
                    best_assignment = (row, col, None)
                for building in self.scenario.available_buildings():
                    if building.name == current_value:
                        continue
                    delta = self.scorer.delta_for_assignment(grid, row, col, building.name)
                    if delta > best_delta:
                        best_delta = delta
                        best_assignment = (row, col, building.name)
            if best_assignment is None or best_delta <= 0:
                return OptimizationResult(grid=grid, score=score, iterations=iteration - 1)
            row, col, value = best_assignment
            grid.set(row, col, value)
            score += best_delta
        return OptimizationResult(grid=grid, score=score, iterations=max_iterations)
