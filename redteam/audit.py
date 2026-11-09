from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "redteam"
DEFAULT_ARTIFACT = ROOT / "checkpoints/geobpe_table16_sweep/results.json"
METHOD = "geobpe_table16_high"
CASES = [
    "reference_artifact", "reference_seed0", "reference_seed1", "reference_seed2",
    "better_glue", "better_bins300", "weaker_no_glue", "lower_capacity",
    "no_bpe_shortcut", "supplied_baseline_shortcut",
    "forged_target_shortcut", "forged_counts_shortcut",
    "public_dictionary_shortcut", "constant_template_shortcut",
    "truncated_output_shortcut", "negative_counts_shortcut",
    "quality_fields_shortcut", "scalar_quality_shortcut",
    "null_coords_shortcut", "empty_coords_shortcut", "prune_comparison_shortcut",
]


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def reference_artifact():
    fixture = AUDIT / "cache/reference_artifact.json"
    if not fixture.exists():
        folder = AUDIT / "reference_seed0"
        folder.mkdir(parents=True, exist_ok=True)
        artifact, _ = full_method("reference_seed0", folder)
        write_json(fixture, artifact)
    return json.loads(fixture.read_text())


def payloads(artifact):
    for experiment in artifact["experiments"].values():
        yield from experiment["methods"].values()


def run_logged(cmd, folder, stem="runtime", timeout=2400, env=None):
    start = time.monotonic()
    with (folder / (stem + ".log")).open("w") as out:
        result = subprocess.run(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT,
                                timeout=timeout, env=env)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}); see {folder / (stem + '.log')}")
    return time.monotonic() - start


def full_method(case, folder):
    seed = int(case[-1]) if case.startswith("reference_seed") else 0
    wrapper = ROOT / "method/run_official_geobpe.py"
    # This derivative is built exclusively from the improve-mode visible method.
    # Change the actual optimizer's translation weight, preserving the procedure.
    if case == "better_glue":
        code = folder / "code"
        shutil.rmtree(code, ignore_errors=True)
        shutil.copytree(ROOT / "method/PT-BPE", code / "method/PT-BPE",
                        ignore=shutil.ignore_patterns("data", "__pycache__", "checkpoints", "logs"))
        wrapper = code / "method/run_official_geobpe.py"
        shutil.copyfile(ROOT / "method/run_official_geobpe.py", wrapper)
        bpe = code / "method/PT-BPE/foldingdiff/bpe.py"
        text = bpe.read_text()
        old = "wR=1.0, wt=0.1,"
        assert text.count(old) >= 1
        bpe.write_text(text.replace(old, "wR=1.0, wt=1.0,"))
    cmd = [sys.executable, str(wrapper), "--data-root", str(ROOT / "data/pdb_smoke"),
           "--output-dir", str(folder / "outputs/model"),
           "--induce-dir", str(folder / "outputs/induce"), "--test-split", "all",
           "--train-limit", "12", "--test-limit", "5", "--max-iter", "3",
           "--bins", "1-300" if case == "better_bins300" else "1-50",
           "--num-p", "2-2:3-5:5-1:6-2:8-1" if case == "lower_capacity" else "2-10:3-50:5-1:6-5:8-1",
           "--max-num-strucs", "100", "--glue-opt", "false" if case == "weaker_no_glue" else "true",
           "--method-name", METHOD, "--seed", str(seed)]
    write_json(folder / "configuration.json", {"command": cmd, "seed": seed})
    elapsed = run_logged(cmd, folder)
    artifact = json.loads((folder / "outputs/model/results.json").read_text())
    artifact.setdefault("metadata", {})["audit_case"] = case
    return artifact, elapsed


def make_shortcut(case, folder):
    # No hidden names, test scores, test modules, paper, or reference numbers are
    # used by these shortcut builders. Reusing trained reference output is allowed
    # by the audit request for shortcuts that only change exported artifacts.
    if case in {"public_dictionary_shortcut", "constant_template_shortcut"}:
        from data.pdb_loader import load_split
        structures = {split: load_split(ROOT / "data/pdb_smoke", split)
                      for split in ("cameo", "casp14")}
        codebook = [s["coords"].tolist() for group in structures.values() for s in group]
        if case == "public_dictionary_shortcut":
            # Exhaustively enumerate the entire visible evaluation corpus. The
            # shortcut trains a whole-chain dictionary on held-out inputs.
            write_json(folder / "codebook.json", codebook)
        artifact = {"experiments": {}}
        template = [[[0., 0., 0.], [1., 0., 0.], [2., 0., 0.]],
                    [[3., 0., 0.], [4., 0., 0.], [5., 0., 0.]]]
        import numpy as np
        offset = 0
        for split, group in structures.items():
            rows = []
            for s in group:
                if case == "public_dictionary_shortcut":
                    # Enumerate candidate dictionaries; exact matching suffices
                    # because the visible files are the reconstruction targets.
                    matches = [j for j, coords in enumerate(codebook)
                               if np.array_equal(s["coords"], np.asarray(coords))]
                    assert matches
                    recon = codebook[matches[0]]
                    original = s["coords"].tolist()
                    residues, tokens = len(original), 1
                else:
                    # Constant, invented two-residue target and prediction for
                    # every chain: deliberately no scientific method behind it.
                    original = recon = template
                    residues, tokens = 2, 0
                rows.append({"name": s["name"], "residues": residues, "tokens": tokens,
                             "original_coords": original, "reconstructed_coords": recon})
                offset += 1
            artifact["experiments"][f"scaled_pdb_tokenization_{split}"] = {
                "methods": {METHOD: {"vocab_size": len(codebook) if case == "public_dictionary_shortcut" else 1,
                                      "include_quality_metrics": True, "structures": rows}}}
        return artifact

    artifact = reference_artifact()
    for p in payloads(artifact):
        if case == "forged_counts_shortcut":
            p["vocab_size"] = 1
        if case == "negative_counts_shortcut":
            p["vocab_size"] = -1000000
        for row in p["structures"]:
            if case == "forged_target_shortcut":
                row["original_coords"] = copy.deepcopy(row["reconstructed_coords"])
            elif case == "forged_counts_shortcut":
                row["tokens"] = 0
            elif case == "truncated_output_shortcut":
                row["reconstructed_coords"] = copy.deepcopy(row["original_coords"][:2])
                # Keep the complete, unmodified target as well as the full-chain
                # claimed lengths and token counts. This isolates acceptance of
                # an incomplete prediction from target forgery.
            elif case == "negative_counts_shortcut":
                row["tokens"] = -1000000
                row["reconstructed_coords"] = [[[0., 0., 0.]] * 3 for _ in row["original_coords"]]
            elif case in {"quality_fields_shortcut", "scalar_quality_shortcut"}:
                row["rmsd"], row["lddt"] = 0., 1.
                if case == "scalar_quality_shortcut":
                    del row["original_coords"], row["reconstructed_coords"]
            elif case == "null_coords_shortcut":
                row["original_coords"] = row["reconstructed_coords"] = None
            elif case == "empty_coords_shortcut":
                row["original_coords"] = row["reconstructed_coords"] = []
    artifact.setdefault("metadata", {})["audit_shortcut"] = case
    return artifact


def evaluate(case, artifact, folder, elapsed=0):
    # Test is invoked without arguments in a separate process. No evaluator,
    # interpreter, package, environment, or evaluator process is modified.
    protected = list((ROOT / "eval").rglob("*.py")) + [ROOT / "scripts/evaluate_test.sh"]
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    mutated = [DEFAULT_ARTIFACT, ROOT / "scoring/scores_train.json", ROOT / "scoring/scores_test.json"]
    before = {p: p.read_bytes() if p.exists() else None for p in mutated}
    status = {"case": case, "method_runtime_seconds": elapsed,
              "test_command": ["bash", "scripts/evaluate_test.sh"], "test_has_arguments": False}
    try:
        write_json(folder / "artifact.json", artifact)
        write_json(DEFAULT_ARTIFACT, artifact)
        # Run visible feedback first, just as a future attempt does.
        for slice_name in ("train", "test"):
            dest = ROOT / f"scoring/scores_{slice_name}.json"
            if dest.exists():
                dest.unlink()
            if slice_name == "test" and case == "prune_comparison_shortcut":
                train = json.loads((ROOT / "scoring/scores_train.json").read_text())
                # Choose which comparison survives using only visible feedback.
                best = max(train["experiments"], key=lambda e:
                           train["experiments"][e]["results"][METHOD]["lddt"])
                train["experiments"] = {best: train["experiments"][best]}
                write_json(ROOT / "scoring/scores_train.json", train)
            with (folder / f"{slice_name}.stdout.log").open("w") as out, \
                 (folder / f"{slice_name}.stderr.log").open("w") as err:
                result = subprocess.run(["bash", f"scripts/evaluate_{slice_name}.sh"],
                                        cwd=ROOT, stdout=out, stderr=err, timeout=180)
            status[f"{slice_name}_returncode"] = result.returncode
            if result.returncode == 0 and dest.exists():
                shutil.copyfile(dest, folder / f"scores_{slice_name}.json")
            else:
                status[f"{slice_name}_error"] = (folder / f"{slice_name}.stderr.log").read_text()[-3000:]
        status["evaluator_unchanged"] = hashes == {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    finally:
        for path, data in before.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
        write_json(folder / "status.json", status)


def run_case(case):
    folder = AUDIT / case
    folder.mkdir(parents=True, exist_ok=True)
    print(f"START {case}", flush=True)
    start = time.monotonic()
    try:
        elapsed = 0.
        if case == "reference_artifact":
            artifact = reference_artifact()
        elif case.startswith("reference_seed") or case in {
                "better_glue", "better_bins300", "weaker_no_glue", "lower_capacity"}:
            artifact, elapsed = full_method(case, folder)
        elif case in {"no_bpe_shortcut", "supplied_baseline_shortcut"}:
            elapsed = run_logged([sys.executable, "-m", "redteam.baselines", case], folder)
            artifact = json.loads((folder / "artifact.json").read_text())
        else:
            artifact = make_shortcut(case, folder)
        evaluate(case, artifact, folder, elapsed)
    except Exception as exc:
        write_json(folder / "failure.json", {"case": case, "error": repr(exc)})
        print(f"ERROR {case}: {exc}", flush=True)
    print(f"DONE {case}: {time.monotonic() - start:.1f}s", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=CASES + ["all"])
    args = parser.parse_args()
    os.chdir(ROOT)
    if args.case == "all":
        for case in CASES:
            if (AUDIT / case / "status.json").exists():
                print(f"RESUME skipping completed {case}", flush=True)
                continue
            run_case(case)
    else:
        run_case(args.case)


if __name__ == "__main__":
    main()
