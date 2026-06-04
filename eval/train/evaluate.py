from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from eval.metrics import summarize_methods


SLICE = "train"
SPLIT_SEED = "2511.11758-geobpe-eval-split-v1"


def _load_experiment_methods(path: str | Path) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text())
    if "experiments" in data:
        return {
            experiment: payload["methods"]
            for experiment, payload in data["experiments"].items()
        }
    return {"scaled_pdb_tokenization_cameo": data["methods"]}


def _row_key(experiment: str, row: dict[str, Any]) -> str:
    name = str(row.get("name", ""))
    residues = str(row.get("residues", ""))
    return f"{SPLIT_SEED}:{experiment}:{name}:{residues}"


def _train_count(experiment: str, row_count: int) -> int:
    if row_count <= 1:
        return row_count
    tie_breaker = int(
        hashlib.sha256(f"{SPLIT_SEED}:count:{experiment}".encode("utf-8")).hexdigest(),
        16,
    ) % 2
    return max(1, min(row_count - 1, row_count // 2 + tie_breaker))


def _select_structure_names(
    experiment: str,
    rows: list[dict[str, Any]],
    slice_name: str,
) -> set[str]:
    keyed = sorted(
        (
            hashlib.sha256(_row_key(experiment, row).encode("utf-8")).hexdigest(),
            str(row.get("name", index)),
        )
        for index, row in enumerate(rows)
    )
    if not keyed:
        return set()
    if len(keyed) == 1:
        return {keyed[0][1]}

    midpoint = _train_count(experiment, len(keyed))
    selected = keyed[:midpoint] if slice_name == "train" else keyed[midpoint:]
    return {name for _, name in selected}


def _filter_methods_for_slice(
    experiment: str,
    methods: dict[str, Any],
    slice_name: str,
) -> dict[str, Any]:
    filtered: dict[str, Any] = {}
    for method_name, payload in methods.items():
        rows = list(payload.get("structures", []))
        selected_names = _select_structure_names(experiment, rows, slice_name)
        selected_rows = [
            row
            for row in rows
            if str(row.get("name", "")) in selected_names
        ]
        if rows and not selected_rows:
            raise ValueError(
                f"{experiment}.{method_name} has no rows selected for {slice_name}"
            )
        filtered_payload = dict(payload)
        filtered_payload["structures"] = selected_rows
        filtered[method_name] = filtered_payload
    return filtered


def summarize_artifact_slice(path: str | Path, slice_name: str) -> dict[str, dict[str, Any]]:
    experiments = _load_experiment_methods(path)
    return {
        experiment: summarize_methods(
            _filter_methods_for_slice(experiment, methods, slice_name)
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
            "split_seed": SPLIT_SEED,
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
