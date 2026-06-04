from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval.metrics import summarize_artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default="checkpoints/geobpe_table16_sweep/results.json")
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()

    experiment_results = summarize_artifact(args.artifact)
    scores = {
        "experiments": {
            experiment: {"results": method_results}
            for experiment, method_results in experiment_results.items()
        }
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
