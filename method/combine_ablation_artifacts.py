from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_method(artifact: Path, experiment: str, method: str) -> dict[str, Any]:
    data = json.loads(artifact.read_text())
    try:
        return data["experiments"][experiment]["methods"][method]
    except KeyError as exc:
        raise KeyError(f"Missing {experiment}/{method} in {artifact}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-glue", default="checkpoints/geobpe_scaled_multisplit/results.json")
    parser.add_argument("--without-glue", required=True)
    parser.add_argument("--output", default="checkpoints/geobpe_glue_ablation/results.json")
    parser.add_argument("--source-experiment", default="scaled_pdb_tokenization_cameo")
    parser.add_argument("--experiment", default="glue_optimization_ablation")
    args = parser.parse_args()

    with_glue_path = Path(args.with_glue)
    without_glue_path = Path(args.without_glue)
    output_path = Path(args.output)

    artifact = {
        "metadata": {
            "source": "official PT-BPE GEOBPE code",
            "ablation": "glue optimization on vs off",
            "with_glue_artifact": str(with_glue_path),
            "without_glue_artifact": str(without_glue_path),
            "source_experiment": args.source_experiment,
        },
        "experiments": {
            args.experiment: {
                "methods": {
                    "geobpe_scaled": load_method(
                        with_glue_path,
                        args.source_experiment,
                        "geobpe_scaled",
                    ),
                    "geobpe_no_glue": load_method(
                        without_glue_path,
                        args.source_experiment,
                        "geobpe_no_glue",
                    ),
                }
            }
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps(artifact, indent=2))


if __name__ == "__main__":
    main()
