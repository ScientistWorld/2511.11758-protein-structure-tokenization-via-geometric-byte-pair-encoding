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


WORKSPACE = Path(__file__).resolve().parents[1]
UPSTREAM = WORKSPACE / "method" / "PT-BPE"
UPSTREAM_DATA = UPSTREAM / "data" / "vqvae_pretrain"


def workspace_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return WORKSPACE / candidate


def str2bool(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    lowered = value.lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean value, got {value!r}")


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


def backbone_coords(coords: Any) -> np.ndarray | None:
    """Normalize N/CA/C backbone coordinates to (residue, atom, xyz)."""
    arr = np.asarray(coords, dtype=float)
    if arr.ndim == 3 and arr.shape[1:] == (3, 3):
        return arr
    if arr.ndim == 2 and arr.shape[1] == 3 and arr.shape[0] % 3 == 0:
        return arr.reshape(-1, 3, 3)
    return None


def latest_iter_checkpoint(output_dir: Path) -> Path:
    candidates = sorted(output_dir.glob("bpe_iter=*.pkl"))
    if not candidates:
        raise FileNotFoundError(f"No BPE iteration checkpoint found in {output_dir}")
    return max(candidates, key=lambda p: int(p.stem.split("=")[1]))


def summarize_induction(induce_dir: Path, bpe: Any) -> dict[str, Any]:
    sys.path.insert(0, str(UPSTREAM))
    rows: list[dict[str, float | int | str]] = []
    for path in sorted(induce_dir.glob("[0-9]*.pkl"), key=lambda p: int(p.stem)):
        stats, tok = load_pickle(path)
        rmsd_values = list(stats["rmsd"])
        lddt_values = list(stats["lddt"])
        length_values = list(stats["L"])
        row: dict[str, Any] = {
            "name": Path(tok.fname).stem,
            "residues": int(tok.n),
            "tokens": int(length_values[-1]),
            "rmsd": float(rmsd_values[-1]),
            "lddt": float(lddt_values[-1]),
        }
        try:
            original_coords = backbone_coords(tok.compute_coords(orig=True))
            reconstructed_coords = backbone_coords(tok.compute_coords())
        except Exception as exc:
            print(f"Skipping coordinate export for {tok.fname}: {exc}", flush=True)
        else:
            if original_coords is not None and reconstructed_coords is not None:
                n_residues = min(len(original_coords), len(reconstructed_coords), int(tok.n))
                row["original_coords"] = original_coords[:n_residues].tolist()
                row["reconstructed_coords"] = reconstructed_coords[:n_residues].tolist()
            else:
                print(
                    f"Skipping coordinate export for {tok.fname}: unexpected coordinate shape",
                    flush=True,
                )
        rows.append(row)
    if not rows:
        raise RuntimeError(f"No induced structure pickles found in {induce_dir}")
    return {
        "geobpe_scaled": {
            "vocab_size": int(bpe.vocab_size),
            "include_quality_metrics": True,
            "structures": rows,
        }
    }


def write_artifact(
    experiments: dict[str, dict[str, Any]],
    bpe_path: Path,
    output_path: Path,
) -> None:
    artifact = {
        "metadata": {
            "source": "official PT-BPE GEOBPE code",
            "upstream_commit": "68ff87eaf13068c1ef93dd72139efe4b91532219",
            "checkpoint": str(bpe_path),
        },
        "experiments": {
            name: {"methods": methods}
            for name, methods in experiments.items()
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
    parser.add_argument(
        "--test-split",
        choices=["cameo", "casp14", "validation", "all"],
        default="cameo",
        help="Held-out split to induce/tokenize after fitting GEOBPE.",
    )
    parser.add_argument("--train-limit", type=int, default=2)
    parser.add_argument("--test-limit", type=int, default=2)
    parser.add_argument("--max-iter", type=int, default=1)
    parser.add_argument("--bins", default="1-50")
    parser.add_argument("--num-p", default="2-10:3-50:5-1:6-5:8-1")
    parser.add_argument("--max-num-strucs", type=int, default=100)
    parser.add_argument("--glue-opt", type=str2bool, default=True)
    parser.add_argument("--method-name", default="geobpe_scaled")
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
    env["PYTHONWARNINGS"] = "ignore::FutureWarning"

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
        str(args.glue_opt),
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
    sys.path.insert(0, str(UPSTREAM))
    bpe = load_pickle(ckpt)
    split_names = ["cameo", "casp14"] if args.test_split == "all" else [args.test_split]
    experiments: dict[str, dict[str, Any]] = {}
    for split_name in split_names:
        split_induce_dir = induce_dir if len(split_names) == 1 else induce_dir / split_name
        split_induce_dir.mkdir(parents=True, exist_ok=True)
        induce_cmd = [
            sys.executable,
            "bin/induce.py",
            "--src-pkl",
            str(ckpt),
            "--save-dir",
            str(split_induce_dir),
            "--log-dir",
            str(WORKSPACE / "logs"),
            "--data-dir",
            {"cameo": "cameo", "casp14": "casp", "validation": "validation"}[split_name],
            "--toy",
            str(args.test_limit),
            "--pad",
            "512",
            "--processed",
            "False",
        ]
        run_command(induce_cmd, env)
        experiment_name = f"scaled_pdb_tokenization_{split_name}"
        methods = summarize_induction(split_induce_dir, bpe)
        if args.method_name != "geobpe_scaled":
            methods = {args.method_name: methods["geobpe_scaled"]}
        experiments[experiment_name] = methods
    write_artifact(experiments, ckpt, output_dir / "results.json")


if __name__ == "__main__":
    main()
