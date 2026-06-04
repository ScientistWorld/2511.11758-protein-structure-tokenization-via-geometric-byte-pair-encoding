from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from eval.metrics import summarize_methods


SLICE = "test"
REQUIRED_STRUCTURES = {
    "scaled_pdb_tokenization_cameo": {"7ctx_B", "7b8b_A", "7ejg_C"},
    "scaled_pdb_tokenization_casp14": {"6n64_A", "6s44_A"},
}


def _load_experiment_methods(path: str | Path) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text())
    if "experiments" in data:
        return {
            experiment: payload["methods"]
            for experiment, payload in data["experiments"].items()
        }
    return {"scaled_pdb_tokenization_cameo": data["methods"]}


def _score_experiments(path: str | Path) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text())
    experiments = data.get("experiments", data)
    normalized: dict[str, dict[str, Any]] = {}
    for experiment, payload in experiments.items():
        if str(experiment).startswith("_") or not isinstance(payload, dict):
            continue
        methods = payload.get("results", payload)
        if isinstance(methods, dict):
            normalized[experiment] = methods
    return normalized


def _filter_methods_for_slice(
    experiment: str,
    methods: dict[str, Any],
    allowed_methods: set[str] | None,
) -> dict[str, Any]:
    required_names = REQUIRED_STRUCTURES.get(experiment)
    if required_names is None:
        raise ValueError(f"No {SLICE} split definition for experiment: {experiment}")

    missing = sorted((allowed_methods or set()) - set(methods))
    if missing:
        raise ValueError(
            f"{experiment} artifact is missing methods present in train scores: "
            + ", ".join(missing)
        )

    method_items = methods.items()
    if allowed_methods is not None:
        method_items = ((name, methods[name]) for name in sorted(allowed_methods))

    filtered: dict[str, Any] = {}
    for method_name, payload in method_items:
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
        missing_rows = sorted(required_names - set(rows_by_name))
        if missing_rows:
            raise ValueError(
                f"{experiment}.{method_name} is missing required {SLICE} "
                "structures: " + ", ".join(missing_rows)
            )
        selected_rows = [rows_by_name[name] for name in sorted(required_names)]
        filtered_payload = dict(payload)
        filtered_payload["structures"] = selected_rows
        filtered[method_name] = filtered_payload
    return filtered


def _train_methods_by_experiment(path: str | Path) -> dict[str, set[str]] | None:
    train_path = Path(path)
    if not train_path.exists():
        return None
    return {
        experiment: {
            method
            for method in methods
            if not str(method).startswith("_")
        }
        for experiment, methods in _score_experiments(train_path).items()
    }


def summarize_artifact_slice(
    path: str | Path,
    slice_name: str,
    train_scores: str | Path,
) -> dict[str, dict[str, Any]]:
    experiments = _load_experiment_methods(path)
    expected_methods = _train_methods_by_experiment(train_scores)
    results: dict[str, dict[str, Any]] = {}
    experiment_names = list(experiments)
    if expected_methods is not None:
        missing_experiments = sorted(set(expected_methods) - set(experiments))
        if missing_experiments:
            raise ValueError(
                "Artifact is missing experiments present in train scores: "
                + ", ".join(missing_experiments)
            )
        experiment_names = [name for name in expected_methods if name in experiments]

    for experiment in experiment_names:
        methods = experiments[experiment]
        allowed_methods = None
        if expected_methods is not None:
            allowed_methods = expected_methods.get(experiment, set())
        results[experiment] = summarize_methods(
            _filter_methods_for_slice(
                experiment,
                methods,
                allowed_methods,
            )
        )
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default="checkpoints/geobpe_scaled_multisplit/results.json")
    parser.add_argument("--train-scores", default="scoring/scores_train.json")
    parser.add_argument("--output", default="scoring/scores_test.json")
    args = parser.parse_args()

    experiment_results = summarize_artifact_slice(args.artifact, SLICE, args.train_scores)
    scores = {
        "_metadata": {
            "slice": SLICE,
            "artifact": str(args.artifact),
            "train_scores": str(args.train_scores),
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
