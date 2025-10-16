from heian_city_optimizer.models import CityScenario
from heian_city_optimizer.optimizer import CityOptimizer


SIMPLE_SCENARIO = {
    "width": 3,
    "height": 3,
    "building_types": [
        {
            "name": "home",
            "base_score": 2,
            "preferred_neighbors": {"park": 1},
            "avoid_neighbors": {"factory": -2},
        },
        {
            "name": "park",
            "base_score": 3,
            "preferred_neighbors": {"home": 1},
            "avoid_neighbors": {},
        },
        {
            "name": "factory",
            "base_score": 4,
            "preferred_neighbors": {"factory": 1},
            "avoid_neighbors": {"home": -3},
        },
    ],
    "initial_grid": [
        ["home", "empty", "empty"],
        ["empty", "empty", "empty"],
        ["park", "empty", "factory"],
    ],
    "locked_cells": [
        [0, 0],
        [2, 0],
        [2, 2],
    ],
}


def test_optimizer_improves_score():
    scenario = CityScenario.from_dict(SIMPLE_SCENARIO)
    optimizer = CityOptimizer(scenario)

    initial_score = optimizer.scorer.total_score(scenario.grid)
    result = optimizer.optimize(max_iterations=100)

    assert result.score >= initial_score
    assert result.iterations > 0
    # ensure the locked cells stay untouched
    assert result.grid.get(0, 0) == "home"
    assert result.grid.get(2, 0) == "park"
    assert result.grid.get(2, 2) == "factory"
