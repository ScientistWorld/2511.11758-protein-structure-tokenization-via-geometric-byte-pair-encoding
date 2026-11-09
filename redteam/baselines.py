from __future__ import annotations

import json
import os
from pathlib import Path
import pickle
import subprocess
import sys

from redteam.audit import AUDIT, ROOT, METHOD, full_method, write_json


def no_bpe_shortcut():
    from method.run_official_geobpe import summarize_induction, prepare_upstream_data
    upstream = ROOT / "method/PT-BPE"
    sys.path.insert(0, str(upstream))
    folder = AUDIT / "no_bpe_shortcut"
    model = AUDIT / "reference_seed0/outputs/model/bpe_post_init.pkl"
    if not model.exists():
        full_method("reference_seed0", AUDIT / "reference_seed0")
    with model.open("rb") as handle:
        bpe = pickle.load(handle)
    prepare_upstream_data(ROOT / "data/pdb_smoke")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(upstream) + os.pathsep + env.get("PYTHONPATH", "")
    env["SLURM_CPUS_PER_TASK"] = "1"
    env["GEOBPE_DATASET_WORKERS"] = "1"
    experiments = {}
    for split, upstream_split in (("cameo", "cameo"), ("casp14", "casp")):
        induce = folder / "outputs" / split
        # No cached tokenizers from other variants are used.
        import shutil
        shutil.rmtree(induce, ignore_errors=True)
        induce.mkdir(parents=True)
        subprocess.run([sys.executable, "bin/induce.py", "--src-pkl", str(model),
                        "--save-dir", str(induce), "--log-dir", str(folder / "logs"),
                        "--data-dir", upstream_split, "--toy", "5", "--pad", "512",
                        "--processed", "False"], cwd=upstream, env=env, check=True)
        payload = summarize_induction(induce, bpe)["geobpe_scaled"]
        experiments[f"scaled_pdb_tokenization_{split}"] = {"methods": {METHOD: payload}}
    write_json(folder / "artifact.json", {"experiments": experiments,
               "metadata": {"shortcut": "no BPE rounds; official residue initialization and glue only",
                            "source": str(model)}})


def supplied_baseline_shortcut():
    # Faithfully run the shipped baseline's model. Its existing exporter omits
    # coordinates, so add them here without changing any predictions.
    from data.pdb_loader import load_split
    from method.geobpe_repro.geobpe import GeoBPE, reconstruct
    train = load_split(ROOT / "data/pdb_smoke", "train", 12)
    model = GeoBPE(residue_k=16, pair_k=1, bins=24, iterations=0, seed=0)
    model.fit(train)
    experiments = {}
    for split in ("cameo", "casp14"):
        rows = []
        for structure in load_split(ROOT / "data/pdb_smoke", split):
            coords = structure["coords"]
            seg = model.encode(coords)
            pred = reconstruct(coords, seg, glue_opt=True)
            rows.append({"name": structure["name"], "residues": len(coords), "tokens": len(seg),
                         "original_coords": coords.tolist(), "reconstructed_coords": pred.tolist()})
        experiments[f"scaled_pdb_tokenization_{split}"] = {
            "methods": {METHOD: {"vocab_size": len(model.vocab),
                                  "include_quality_metrics": True, "structures": rows}}}
    write_json(AUDIT / "supplied_baseline_shortcut/artifact.json", {
        "experiments": experiments, "metadata": {
            "shortcut": "shipped baseline uses uncharged continuous frame glue",
            "implementation": "baseline/residue_quantized.py -> residue_baseline"}})


if __name__ == "__main__":
    {"no_bpe_shortcut": no_bpe_shortcut,
     "supplied_baseline_shortcut": supplied_baseline_shortcut}[sys.argv[1]]()
