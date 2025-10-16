import json
import subprocess
import sys
from pathlib import Path


def test_cli_runs_and_writes_output(tmp_path: Path):
    scenario_path = Path(__file__).resolve().parents[1] / "scenarios" / "sample_scenario.json"
    output_path = tmp_path / "result.json"

    command = [
        sys.executable,
        "-m",
        "heian_city_optimizer.cli",
        "optimize",
        str(scenario_path),
        "--iterations",
        "50",
        "--show-grid",
        "--output",
        str(output_path),
    ]

    completed = subprocess.run(command, check=True, capture_output=True, text=True)

    assert "Optimized score" in completed.stdout
    assert output_path.exists()

    data = json.loads(output_path.read_text())
    assert "score" in data
    assert "grid" in data
