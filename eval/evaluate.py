from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval.metrics import summarize_artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default="checkpoints/geobpe_scaled/results.json")
    parser.add_argument("--output", default="scoring/scores.json")
    args = parser.parse_args()

    method_results = summarize_artifact(args.artifact)
    scores = {
        "experiments": {
            "scaled_pdb_tokenization": {
                "results": method_results,
            }
        }
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(scores, indent=2) + "\n")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
