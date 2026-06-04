from __future__ import annotations

import argparse
import json
import os
import pickle
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np


WORKSPACE = Path("/home/user")
UPSTREAM = WORKSPACE / "method" / "PT-BPE"
UPSTREAM_DATA = UPSTREAM / "data" / "vqvae_pretrain"


def workspace_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return WORKSPACE / candidate


def _link_or_copy(src: Path, dst: Path) -> None:
    if dst.is_symlink() or dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        dst.symlink_to(src)
    except OSError:
        shutil.copytree(src, dst)


def prepare_upstream_data(data_root: Path) -> None:
    mapping = {
        "train": "train",
        "validation": "validation",
        "CAMEO": "cameo",
        "CASP14": "casp14",
    }
    for upstream_name, local_name in mapping.items():
        src = data_root / local_name
        if not src.exists():
            raise FileNotFoundError(f"Missing local split: {src}")
        _link_or_copy(src.resolve(), UPSTREAM_DATA / upstream_name)


def run_command(cmd: list[str], env: dict[str, str]) -> None:
    print("+ " + " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=UPSTREAM, env=env, check=True)


def load_pickle(path: Path) -> Any:
    with path.open("rb") as handle:
        return pickle.load(handle)


def latest_iter_checkpoint(output_dir: Path) -> Path:
    candidates = sorted(output_dir.glob("bpe_iter=*.pkl"))
    if not candidates:
        raise FileNotFoundError(f"No BPE iteration checkpoint found in {output_dir}")
    return max(candidates, key=lambda p: int(p.stem.split("=")[1]))


def summarize_induction(induce_dir: Path, bpe_path: Path, output_path: Path) -> None:
    sys.path.insert(0, str(UPSTREAM))
    bpe = load_pickle(bpe_path)
    rows: list[dict[str, float | int | str]] = []
    for path in sorted(induce_dir.glob("[0-9]*.pkl"), key=lambda p: int(p.stem)):
        stats, tok = load_pickle(path)
        rmsd_values = list(stats["rmsd"])
        lddt_values = list(stats["lddt"])
        length_values = list(stats["L"])
        original_coords = np.asarray(tok._coords, dtype=float).reshape(-1, 3, 3)
        reconstructed_coords = np.asarray(tok.compute_coords(), dtype=float).reshape(-1, 3, 3)
        rows.append(
            {
                "name": Path(tok.fname).stem,
                "residues": int(tok.n),
                "tokens": int(length_values[-1]),
                "rmsd": float(rmsd_values[-1]),
                "lddt": float(lddt_values[-1]),
                "original_coords": original_coords.tolist(),
                "reconstructed_coords": reconstructed_coords.tolist(),
            }
        )
    if not rows:
        raise RuntimeError(f"No induced structure pickles found in {induce_dir}")
    artifact = {
        "metadata": {
            "source": "official PT-BPE GEOBPE code",
            "upstream_commit": "68ff87eaf13068c1ef93dd72139efe4b91532219",
            "checkpoint": str(bpe_path),
        },
        "methods": {
            "geobpe_scaled": {
                "vocab_size": int(bpe.vocab_size),
                "include_quality_metrics": True,
                "structures": rows,
            }
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2) + "\n")
    print(json.dumps(artifact, indent=2), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default=str(WORKSPACE / "data" / "pdb_smoke"))
    parser.add_argument("--output-dir", default=str(WORKSPACE / "checkpoints" / "geobpe_scaled"))
    parser.add_argument("--induce-dir", default=str(WORKSPACE / "checkpoints" / "geobpe_scaled_cameo"))
    parser.add_argument("--train-limit", type=int, default=2)
    parser.add_argument("--test-limit", type=int, default=2)
    parser.add_argument("--max-iter", type=int, default=1)
    parser.add_argument("--bins", default="1-50")
    parser.add_argument("--num-p", default="2-10:3-50:5-1:6-5:8-1")
    parser.add_argument("--max-num-strucs", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    if not (UPSTREAM / "bin" / "encode.py").exists():
        raise FileNotFoundError(f"Official PT-BPE code is missing at {UPSTREAM}")

    output_dir = workspace_path(args.output_dir)
    induce_dir = workspace_path(args.induce_dir)
    shutil.rmtree(output_dir, ignore_errors=True)
    shutil.rmtree(induce_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    induce_dir.mkdir(parents=True, exist_ok=True)
    prepare_upstream_data(workspace_path(args.data_root))

    env = os.environ.copy()
    env["PYTHONPATH"] = f"{UPSTREAM}:{env.get('PYTHONPATH', '')}"
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    env.setdefault("GEOBPE_DATASET_WORKERS", "1")
    env["SLURM_CPUS_PER_TASK"] = "1"

    encode_cmd = [
        sys.executable,
        "bin/encode.py",
        "--data-dir",
        "pretrain",
        "--toy",
        str(args.train_limit),
        "--pad",
        "512",
        "--save-dir",
        str(output_dir),
        "--log-dir",
        str(WORKSPACE / "logs"),
        "--vis",
        "False",
        "--num-vis",
        "1",
        "--num-ref",
        str(max(1, min(args.train_limit, 2))),
        "--res-init",
        "True",
        "--free-bonds",
        "False",
        "--rmsd-super-res",
        "False",
        "--rmsd-only",
        "False",
        "--bin-strategy",
        "histogram",
        "--bins",
        args.bins,
        "--sec",
        "False",
        "--sec-eval",
        "False",
        "--p-min-size",
        "2",
        "--num-p",
        args.num_p,
        "--max-num-strucs",
        str(args.max_num_strucs),
        "--glue-opt",
        "True",
        "--glue-opt-prior",
        "0.0",
        "--glue-opt-every",
        "1",
        "--glue-opt-method",
        "all",
        "--save-every",
        "1",
        "--plot-every",
        "1000",
        "--max-iter",
        str(args.max_iter),
        "--seed",
        str(args.seed),
    ]
    run_command(encode_cmd, env)

    ckpt = latest_iter_checkpoint(output_dir)
    induce_cmd = [
        sys.executable,
        "bin/induce.py",
        "--src-pkl",
        str(ckpt),
        "--save-dir",
        str(induce_dir),
        "--log-dir",
        str(WORKSPACE / "logs"),
        "--data-dir",
        "cameo",
        "--toy",
        str(args.test_limit),
        "--pad",
        "512",
        "--processed",
        "False",
    ]
    run_command(induce_cmd, env)
    summarize_induction(induce_dir, ckpt, output_dir / "results.json")


if __name__ == "__main__":
    main()
