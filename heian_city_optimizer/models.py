"""Data models for the Heian City Optimizer."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple
import json


Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class BuildingType:
    """Represents a type of building that can appear in the city grid."""

    name: str
    base_score: float
    preferred_neighbors: Dict[str, float] = field(default_factory=dict)
    avoid_neighbors: Dict[str, float] = field(default_factory=dict)

    @staticmethod
    def from_dict(raw: Dict[str, object]) -> "BuildingType":
        """Create a :class:`BuildingType` from raw dictionary data."""
        name = str(raw["name"])
        base_score = float(raw.get("base_score", 0.0))
        preferred = {
            str(key): float(value)
            for key, value in dict(raw.get("preferred_neighbors", {})).items()
        }
        avoid = {
            str(key): float(value)
            for key, value in dict(raw.get("avoid_neighbors", {})).items()
        }
        return BuildingType(name=name, base_score=base_score, preferred_neighbors=preferred, avoid_neighbors=avoid)


class CityGrid:
    """Mutable representation of the city grid."""

    def __init__(self, width: int, height: int, cells: Optional[Sequence[Sequence[Optional[str]]]] = None) -> None:
        self.width = width
        self.height = height
        if cells is None:
            self._cells: List[List[Optional[str]]] = [[None for _ in range(width)] for _ in range(height)]
        else:
            if len(cells) != height:
                raise ValueError("Cell data does not match grid height")
            processed: List[List[Optional[str]]] = []
            for row in cells:
                if len(row) != width:
                    raise ValueError("Cell data does not match grid width")
                processed.append([self._normalize_value(value) for value in row])
            self._cells = processed

    @staticmethod
    def _normalize_value(value: Optional[str]) -> Optional[str]:
        if value in (None, "", "empty"):
            return None
        return str(value)

    def copy(self) -> "CityGrid":
        return CityGrid(self.width, self.height, [row[:] for row in self._cells])

    def get(self, row: int, col: int) -> Optional[str]:
        return self._cells[row][col]

    def set(self, row: int, col: int, value: Optional[str]) -> None:
        self._cells[row][col] = self._normalize_value(value)

    def iter_coords(self) -> Iterator[Coordinate]:
        for row in range(self.height):
            for col in range(self.width):
                yield (row, col)

    def neighbors(self, row: int, col: int) -> Iterator[Coordinate]:
        if row > 0:
            yield (row - 1, col)
        if row < self.height - 1:
            yield (row + 1, col)
        if col > 0:
            yield (row, col - 1)
        if col < self.width - 1:
            yield (row, col + 1)

    def to_matrix(self) -> List[List[Optional[str]]]:
        return [row[:] for row in self._cells]

    def to_serializable(self, empty_token: str = "empty") -> List[List[str]]:
        matrix: List[List[str]] = []
        for row in self._cells:
            matrix.append([cell if cell is not None else empty_token for cell in row])
        return matrix

    def __str__(self) -> str:  # pragma: no cover - convenience method
        rows = [
            " | ".join(cell if cell is not None else "--" for cell in row)
            for row in self._cells
        ]
        return "\n".join(rows)


@dataclass
class CityScenario:
    """Complete description of an optimization scenario."""

    grid: CityGrid
    building_types: Dict[str, BuildingType]
    locked_cells: Sequence[Coordinate] = field(default_factory=tuple)
    _locked_set: frozenset[Coordinate] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        normalized: List[Coordinate] = []
        for coord in self.locked_cells:
            row, col = coord
            normalized.append((int(row), int(col)))
        self.locked_cells = tuple(normalized)
        self._locked_set = frozenset(self.locked_cells)

    @property
    def locked_set(self) -> frozenset[Coordinate]:
        return self._locked_set

    def is_locked(self, coord: Coordinate) -> bool:
        return coord in self.locked_set

    @staticmethod
    def from_dict(raw: Dict[str, object]) -> "CityScenario":
        width = int(raw["width"])
        height = int(raw["height"])
        building_types = {
            data["name"]: BuildingType.from_dict(data)
            for data in raw.get("building_types", [])
        }
        if not building_types:
            raise ValueError("Scenario must define at least one building type")

        raw_grid = raw.get("initial_grid")
        if raw_grid is None:
            grid = CityGrid(width, height)
        else:
            grid = CityGrid(width, height, raw_grid)  # type: ignore[arg-type]

        locked_cells = [tuple(coords) for coords in raw.get("locked_cells", [])]

        scenario = CityScenario(grid=grid, building_types=building_types, locked_cells=locked_cells)
        for row, col in scenario.grid.iter_coords():
            value = scenario.grid.get(row, col)
            if value is not None:
                scenario.ensure_valid_building(value)
        return scenario

    @staticmethod
    def from_path(path: Path | str) -> "CityScenario":
        data = json.loads(Path(path).read_text())
        return CityScenario.from_dict(data)

    def available_buildings(self) -> Iterable[BuildingType]:
        return self.building_types.values()

    def ensure_valid_building(self, name: Optional[str]) -> Optional[str]:
        if name is None:
            return None
        name = str(name)
        if name not in self.building_types:
            raise KeyError(f"Unknown building type '{name}'")
        return name
