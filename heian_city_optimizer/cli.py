"""Command line interface for the Heian City Optimizer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .models import CityScenario
from .optimizer import CityOptimizer


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="heian-city-optimizer", description="Optimize layouts for Heian city planning scenarios.")
    subparsers = parser.add_subparsers(dest="command")

    optimize_parser = subparsers.add_parser("optimize", help="Optimize a scenario described in JSON format.")
    optimize_parser.add_argument("scenario", type=Path, help="Path to the scenario JSON file.")
    optimize_parser.add_argument("--iterations", type=int, default=200, help="Maximum optimizer iterations (default: 200).")
    optimize_parser.add_argument("--show-grid", action="store_true", help="Display the resulting grid in ASCII form.")
    optimize_parser.add_argument("--output", type=Path, help="Optional path to write the optimized grid as JSON.")

    return parser


def _handle_optimize(args: argparse.Namespace) -> int:
    scenario = CityScenario.from_path(args.scenario)
    optimizer = CityOptimizer(scenario)
    result = optimizer.optimize(max_iterations=args.iterations)

    print(f"Optimized score: {result.score:.2f}")
    print(f"Iterations performed: {result.iterations}")

    if args.show_grid:
        print("\nOptimized grid:")
        print(result.render_ascii())

    if args.output:
        data: dict[str, Any] = result.to_dict()
        args.output.write_text(json.dumps(data, indent=2))
        print(f"\nWritten optimized scenario to {args.output}")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "optimize":
        return _handle_optimize(args)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
