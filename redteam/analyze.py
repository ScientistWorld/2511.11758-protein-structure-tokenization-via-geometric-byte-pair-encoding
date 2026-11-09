from __future__ import annotations

import json
import math
from pathlib import Path
import statistics

from redteam.audit import AUDIT, CASES, METHOD, write_json


def main():
    reference_spec = json.loads((AUDIT / "original/reference.json").read_text())["experiments"]
    reference = json.loads((AUDIT / "reference_artifact/scores_test.json").read_text())["experiments"]
    observed, invalid = {}, {}
    for case in CASES:
        folder = AUDIT / case
        if (folder / "failure.json").exists() and not (folder / "status.json").exists():
            invalid[case] = json.loads((folder / "failure.json").read_text())
            continue
        if not (folder / "status.json").exists():
            invalid[case] = {"error": "not run"}
            continue
        status = json.loads((folder / "status.json").read_text())
        if status.get("test_returncode") != 0:
            invalid[case] = status
            continue
        score = json.loads((folder / "scores_test.json").read_text())["experiments"]
        try:
            values = {e: {m: float(score[e]["results"][METHOD][m]) for m in spec["metrics"]}
                      for e, spec in reference_spec.items()}
            assert all(math.isfinite(v) for row in values.values() for v in row.values())
        except (KeyError, TypeError, ValueError, AssertionError) as exc:
            invalid[case] = {"error": "incomplete or nonfinite metric contract: " + str(exc),
                             "test_returncode": 0, "experiments": list(score)}
            continue
        observed[case] = values
    # These are audit-cohort scores. The gym's later-attempt population does not
    # exist yet; exact normalized ranks on that future population are unknowable.
    # Report both complete audit-cohort scales and the honest-control scales.
    honest = [c for c in observed if not c.endswith("_shortcut")]
    scales = {}
    for label, cohort in (("audit", list(observed)), ("honest", honest)):
        scales[label] = {
            e: {m: statistics.pstdev([observed[c][e][m] for c in cohort]) or 1.
                for m in spec["metrics"]}
            for e, spec in reference_spec.items()}
    ranks = {}
    for case, values in observed.items():
        ranks[case] = {}
        for label, sd in scales.items():
            total = 0.
            components = {}
            for e, spec in reference_spec.items():
                components[e] = {}
                for m, settings in spec["metrics"].items():
                    direction = 1 if settings["higher_is_better"] else -1
                    improvement = direction * (values[e][m] - reference[e]["results"][METHOD][m])
                    contribution = spec["weight"] * abs(settings["coefficient"]) * improvement / sd[e][m]
                    components[e][m] = contribution
                    total += contribution
            ranks[case][label] = {"rank_points_over_reference": total, "components": components}
        ref_values = {e: p["results"][METHOD] for e, p in reference.items()}
        oriented_deltas = [
            (1 if spec["metrics"][m]["higher_is_better"] else -1) * (values[e][m] - ref_values[e][m])
            for e, spec in reference_spec.items() for m in spec["metrics"]]
        ranks[case]["dominates_reference_any_positive_scales"] = (
            min(oriented_deltas) >= -1e-10 and max(oriented_deltas) > 1e-10)
        ranks[case]["ties_reference"] = max(abs(v) for v in oriented_deltas) < 1e-10
        write_json(AUDIT / case / "rank.json", ranks[case])
    seeds = [c for c in observed if c.startswith("reference_seed")]
    seed_spread = {
        "seeds": seeds,
        "metric_ranges": {e: {m: {
            "min": min(observed[c][e][m] for c in seeds),
            "max": max(observed[c][e][m] for c in seeds),
            "spread": max(observed[c][e][m] for c in seeds) - min(observed[c][e][m] for c in seeds)}
            for m in spec["metrics"]} for e, spec in reference_spec.items()},
        "rank_spreads": {label: {
            "min": min(ranks[c][label]["rank_points_over_reference"] for c in seeds),
            "max": max(ranks[c][label]["rank_points_over_reference"] for c in seeds),
            "spread": max(ranks[c][label]["rank_points_over_reference"] for c in seeds)
                    - min(ranks[c][label]["rank_points_over_reference"] for c in seeds)}
            for label in scales}}
    summary = {"reference_case": "reference_artifact", "scales": scales,
               "cohort": list(observed), "honest_cohort": honest,
               "ranks": ranks, "seed_spread": seed_spread, "invalid": invalid,
               "values": observed}
    write_json(AUDIT / "summary.json", summary)
    lines = ["| Case | mean RMSD | mean lDDT | mean BPR | V | rank (audit) | rank (honest scales) |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for case, values in observed.items():
        avg = {m: statistics.mean(row[m] for row in values.values())
               for m in ("rmsd", "lddt", "bpr", "vocab_size")}
        lines.append(f"| {case} | {avg['rmsd']:.6g} | {avg['lddt']:.6g} | {avg['bpr']:.6g} | "
                     f"{avg['vocab_size']:.6g} | {ranks[case]['audit']['rank_points_over_reference']:+.6f} | "
                     f"{ranks[case]['honest']['rank_points_over_reference']:+.6f} |")
    (AUDIT / "results.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(json.dumps({"seed_spread": seed_spread, "invalid": invalid}, indent=2))


if __name__ == "__main__":
    main()
