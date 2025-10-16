"""Scoring helpers for the Heian City Optimizer."""
from __future__ import annotations

from typing import Iterable, Optional, Tuple

from .models import CityGrid, CityScenario


class CityScorer:
    """Calculate scores for a grid configuration."""

    def __init__(self, scenario: CityScenario) -> None:
        self.scenario = scenario

    def cell_score(self, grid: CityGrid, row: int, col: int) -> float:
        """Compute the score contribution for a single cell."""
        name = grid.get(row, col)
        if name is None:
            return 0.0
        building = self.scenario.building_types[name]
        score = building.base_score
        for n_row, n_col in grid.neighbors(row, col):
            neighbor_name = grid.get(n_row, n_col)
            if neighbor_name is None:
                continue
            score += building.preferred_neighbors.get(neighbor_name, 0.0)
            score += building.avoid_neighbors.get(neighbor_name, 0.0)
        return score

    def total_score(self, grid: CityGrid) -> float:
        return sum(self.cell_score(grid, row, col) for row, col in grid.iter_coords())

    def _affected_cells(self, grid: CityGrid, row: int, col: int) -> Iterable[Tuple[int, int]]:
        yield (row, col)
        yield from grid.neighbors(row, col)

    def delta_for_assignment(self, grid: CityGrid, row: int, col: int, new_value: Optional[str]) -> float:
        """Compute the score delta when assigning ``new_value`` to ``(row, col)``."""
        new_value = self.scenario.ensure_valid_building(new_value)
        affected = list(self._affected_cells(grid, row, col))
        before = sum(self.cell_score(grid, r, c) for r, c in affected)
        original_value = grid.get(row, col)
        grid.set(row, col, new_value)
        after = sum(self.cell_score(grid, r, c) for r, c in affected)
        grid.set(row, col, original_value)
        return after - before
