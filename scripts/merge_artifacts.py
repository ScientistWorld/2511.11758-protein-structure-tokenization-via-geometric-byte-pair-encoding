from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_experiments(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text())
    if "experiments" in data:
        return {
            experiment: payload["methods"]
            for experiment, payload in data["experiments"].items()
        }
    return {"scaled_pdb_tokenization_cameo": data["methods"]}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge method artifacts into one evaluator artifact."
    )
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Artifact spec as PATH:OLD_METHOD:NEW_METHOD.",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    merged: dict[str, dict[str, dict[str, Any]]] = {}
    sources: list[dict[str, str]] = []
    for spec in args.input:
        parts = spec.split(":")
        if len(parts) != 3:
            raise ValueError(f"Expected PATH:OLD_METHOD:NEW_METHOD, got {spec!r}")
        path_text, old_method, new_method = parts
        path = Path(path_text)
        experiments = load_experiments(path)
        sources.append(
            {
                "artifact": str(path),
                "old_method": old_method,
                "new_method": new_method,
            }
        )
        for experiment, methods in experiments.items():
            if old_method not in methods:
                raise KeyError(f"{path} missing method {old_method!r} in {experiment}")
            merged.setdefault(experiment, {})[new_method] = methods[old_method]

    artifact = {
        "metadata": {
            "source": "merged GEOBPE reproduction artifacts",
            "sources": sources,
        },
        "experiments": {
            experiment: {"methods": methods}
            for experiment, methods in sorted(merged.items())
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2) + "\n")
    method_summary = {
        experiment: sorted(methods)
        for experiment, methods in sorted(merged.items())
    }
    print(f"Wrote merged artifact to {output}")
    print(json.dumps({"experiments": method_summary}, indent=2))


if __name__ == "__main__":
    main()
