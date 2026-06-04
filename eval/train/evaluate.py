from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from eval.metrics import summarize_methods


SLICE = "train"
REQUIRED_STRUCTURES = {
    "scaled_pdb_tokenization_cameo": {"7egt_B", "7dri_A"},
    "scaled_pdb_tokenization_casp14": {"6px4_T", "6px4_R", "6poo_A"},
}


def _load_experiment_methods(path: str | Path) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text())
    if "experiments" in data:
        return {
            experiment: payload["methods"]
            for experiment, payload in data["experiments"].items()
        }
    return {"scaled_pdb_tokenization_cameo": data["methods"]}


def _filter_methods_for_slice(
    experiment: str,
    methods: dict[str, Any],
) -> dict[str, Any]:
    required_names = REQUIRED_STRUCTURES.get(experiment)
    if required_names is None:
        raise ValueError(f"No {SLICE} split definition for experiment: {experiment}")

    filtered: dict[str, Any] = {}
    for method_name, payload in methods.items():
        rows = list(payload.get("structures", []))
        row_names = [str(row.get("name", "")) for row in rows]
        duplicate_names = sorted(
            {name for name in row_names if row_names.count(name) > 1}
        )
        if duplicate_names:
            raise ValueError(
                f"{experiment}.{method_name} has duplicate structure rows: "
                + ", ".join(duplicate_names)
            )
        rows_by_name = {str(row.get("name", "")): row for row in rows}
        missing = sorted(required_names - set(rows_by_name))
        if missing:
            raise ValueError(
                f"{experiment}.{method_name} is missing required {SLICE} "
                "structures: " + ", ".join(missing)
            )
        selected_rows = [rows_by_name[name] for name in sorted(required_names)]
        filtered_payload = dict(payload)
        filtered_payload["structures"] = selected_rows
        filtered[method_name] = filtered_payload
    return filtered


def summarize_artifact_slice(path: str | Path, slice_name: str) -> dict[str, dict[str, Any]]:
    experiments = _load_experiment_methods(path)
    return {
        experiment: summarize_methods(
            _filter_methods_for_slice(experiment, methods)
        )
        for experiment, methods in experiments.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default="checkpoints/geobpe_scaled_multisplit/results.json")
    parser.add_argument("--output", default="scoring/scores_train.json")
    args = parser.parse_args()

    experiment_results = summarize_artifact_slice(args.artifact, SLICE)
    scores = {
        "_metadata": {
            "slice": SLICE,
            "artifact": str(args.artifact),
            "required_structures": {
                experiment: sorted(names)
                for experiment, names in REQUIRED_STRUCTURES.items()
            },
        },
        "experiments": {
            experiment: {"results": method_results}
            for experiment, method_results in experiment_results.items()
        },
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
