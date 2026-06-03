from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from data.pdb_loader import load_split
from eval.metrics import ca_lddt, kabsch_align, rmsd


def canonical(coords: np.ndarray) -> np.ndarray:
    """Represent a motif in the local frame of its first residue."""
    r, t = residue_frame(coords[0])
    flat = coords.reshape(-1, 3)
    local = (r.T @ (flat - t).T).T
    return local.reshape(coords.shape)


def residue_frame(residue: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return a right-handed residue frame as local-to-world rotation and origin."""
    n, ca, c = residue
    x = c - ca
    x = x / max(np.linalg.norm(x), 1e-8)
    y_raw = n - ca
    y = y_raw - np.dot(y_raw, x) * x
    y = y / max(np.linalg.norm(y), 1e-8)
    z = np.cross(x, y)
    z = z / max(np.linalg.norm(z), 1e-8)
    y = np.cross(z, x)
    r = np.stack([x, y, z], axis=1)
    return r, ca.copy()


def relative_frame(left_residue: np.ndarray, right_residue: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """SE(3) transform from the left residue frame to the right residue frame."""
    r_left, t_left = residue_frame(left_residue)
    r_right, t_right = residue_frame(right_residue)
    return r_left.T @ r_right, r_left.T @ (t_right - t_left)


def place_in_frame(coords: np.ndarray, frame: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    """Place canonical motif coordinates in a world residue frame."""
    r, t = frame
    flat = coords.reshape(-1, 3)
    placed = (r @ flat.T).T + t
    return placed.reshape(coords.shape)


def kabsch_rmsd(a: np.ndarray, b: np.ndarray) -> float:
    return rmsd(a, b)


def kmedoids(fragments: list[np.ndarray], k: int, seed: int = 0, max_iter: int = 8) -> tuple[list[int], list[int]]:
    n = len(fragments)
    k = max(1, min(k, n))
    rng = np.random.default_rng(seed)
    medoids = sorted(rng.choice(n, size=k, replace=False).tolist())
    dmat = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(i + 1, n):
            dmat[i, j] = dmat[j, i] = kabsch_rmsd(fragments[i], fragments[j])
    labels = [0] * n
    for _ in range(max_iter):
        labels = [int(np.argmin([dmat[i, m] for m in medoids])) for i in range(n)]
        new_medoids = medoids[:]
        for c in range(k):
            members = [i for i, label in enumerate(labels) if label == c]
            if not members:
                new_medoids[c] = int(rng.integers(0, n))
                continue
            costs = [sum(dmat[i, j] for j in members) for i in members]
            new_medoids[c] = members[int(np.argmin(costs))]
        if new_medoids == medoids:
            break
        medoids = new_medoids
    labels = [int(np.argmin([dmat[i, m] for m in medoids])) for i in range(n)]
    return medoids, labels


def discretize_boundary(left: np.ndarray, right: np.ndarray, bins: int) -> tuple[int, int, int]:
    # A compact glue key: distance and two CA direction angles across the motif boundary.
    v = right[0, 1] - left[-1, 1]
    dist = np.linalg.norm(v)
    theta = math.atan2(v[1], v[0]) % (2 * math.pi)
    phi = math.atan2(v[2], max(np.linalg.norm(v[:2]), 1e-8)) + math.pi / 2
    return (
        min(bins - 1, int(dist / 20.0 * bins)),
        min(bins - 1, int(theta / (2 * math.pi) * bins)),
        min(bins - 1, int(phi / math.pi * bins)),
    )


@dataclass
class Motif:
    start: int
    end: int
    token: int
    coords: np.ndarray
    glue_from_prev: tuple[np.ndarray, np.ndarray] | None = None


class GeoBPE:
    def __init__(self, residue_k: int, pair_k: int, bins: int, iterations: int, seed: int = 0):
        self.residue_k = residue_k
        self.pair_k = pair_k
        self.bins = bins
        self.iterations = iterations
        self.seed = seed
        self.vocab: dict[int, np.ndarray] = {}
        self.merge_order: list[tuple[tuple, list[int]]] = []
        self.next_token = 0

    def _new_token(self, proto: np.ndarray) -> int:
        tok = self.next_token
        self.next_token += 1
        self.vocab[tok] = canonical(proto)
        return tok

    def _init_residues(self, structures: list[dict]) -> list[list[Motif]]:
        residues = [s["coords"][i : i + 1] for s in structures for i in range(len(s["coords"]))]
        medoids, labels = kmedoids(residues, self.residue_k, self.seed)
        residue_tokens = [self._new_token(residues[idx]) for idx in medoids]
        segmentations = []
        offset = 0
        for s in structures:
            seg = []
            for i in range(len(s["coords"])):
                tok = residue_tokens[labels[offset]]
                glue = None
                if i > 0:
                    glue = relative_frame(s["coords"][i - 1], s["coords"][i])
                seg.append(Motif(i, i + 1, tok, self.vocab[tok].copy(), glue))
                offset += 1
            segmentations.append(seg)
        return segmentations

    def _pair_key(self, left: Motif, right: Motif) -> tuple:
        return (left.token, discretize_boundary(left.coords, right.coords, self.bins), right.token)

    def _collect_pairs(self, segmentations: list[list[Motif]]) -> dict[tuple, list[tuple[int, int]]]:
        pairs = defaultdict(list)
        for si, seg in enumerate(segmentations):
            for pi in range(len(seg) - 1):
                pairs[self._pair_key(seg[pi], seg[pi + 1])].append((si, pi))
        return pairs

    def fit(self, structures: list[dict]) -> list[list[Motif]]:
        segmentations = self._init_residues(structures)
        for step in range(self.iterations):
            pairs = self._collect_pairs(segmentations)
            if not pairs:
                break
            key, occs = max(pairs.items(), key=lambda item: (len(item[1]), str(item[0])))
            fragments = []
            valid = []
            for si, pi in occs:
                seg = segmentations[si]
                if pi + 1 < len(seg) and self._pair_key(seg[pi], seg[pi + 1]) == key:
                    fragments.append(structures[si]["coords"][seg[pi].start : seg[pi + 1].end])
                    valid.append((si, pi))
            if len(fragments) < 2:
                break
            medoids, labels = kmedoids(fragments, min(self.pair_k, len(fragments)), self.seed + step + 1)
            new_tokens = [self._new_token(fragments[idx]) for idx in medoids]
            self.merge_order.append((key, new_tokens))

            by_pos = defaultdict(dict)
            for occ, label in zip(valid, labels):
                by_pos[occ[0]][occ[1]] = new_tokens[label]
            for si, positions in by_pos.items():
                old = segmentations[si]
                merged = []
                i = 0
                while i < len(old):
                    if i in positions and i + 1 < len(old) and self._pair_key(old[i], old[i + 1]) == key:
                        tok = positions[i]
                        merged.append(
                            Motif(
                                old[i].start,
                                old[i + 1].end,
                                tok,
                                self.vocab[tok].copy(),
                                old[i].glue_from_prev,
                            )
                        )
                        i += 2
                    else:
                        merged.append(old[i])
                        i += 1
                segmentations[si] = merged
        return segmentations

    def encode(self, coords: np.ndarray) -> list[Motif]:
        seg = []
        residue_protos = list(range(self.residue_k))
        for i in range(len(coords)):
            frag = coords[i : i + 1]
            tok = min(residue_protos, key=lambda t: kabsch_rmsd(frag, self.vocab[t]))
            glue = None
            if i > 0:
                glue = relative_frame(coords[i - 1], coords[i])
            seg.append(Motif(i, i + 1, tok, self.vocab[tok].copy(), glue))
        for key, tokens in self.merge_order:
            i = 0
            new_seg = []
            while i < len(seg):
                if i + 1 < len(seg) and self._pair_key(seg[i], seg[i + 1]) == key:
                    raw = coords[seg[i].start : seg[i + 1].end]
                    tok = min(tokens, key=lambda t: kabsch_rmsd(raw, self.vocab[t]))
                    new_seg.append(
                        Motif(
                            seg[i].start,
                            seg[i + 1].end,
                            tok,
                            self.vocab[tok].copy(),
                            seg[i].glue_from_prev,
                        )
                    )
                    i += 2
                else:
                    new_seg.append(seg[i])
                    i += 1
            seg = new_seg
        return seg


def reconstruct(original: np.ndarray, seg: list[Motif], glue_opt: bool) -> np.ndarray:
    if glue_opt:
        # Decoder analogue of GEOBPE glue: compose quantized motif prototypes with
        # the inter-motif frame transforms emitted by the encoder. This preserves
        # each medoid shape and uses only boundary glue, not per-span target fitting.
        pieces = []
        frame = residue_frame(original[0])
        for idx, motif in enumerate(seg):
            if idx > 0 and motif.glue_from_prev is not None:
                r_rel, t_rel = motif.glue_from_prev
                r_prev, t_prev = residue_frame(pieces[-1][-1])
                frame = (r_prev @ r_rel, t_prev + r_prev @ t_rel)
            pieces.append(place_in_frame(motif.coords, frame))
        return np.concatenate(pieces, axis=0)
    # No-glue ablation assembles prototypes in canonical frames, exposing drift.
    assembled = []
    cursor = original[0, 1].copy()
    for motif in seg:
        block = motif.coords.copy()
        block = block - block[0, 1] + cursor
        assembled.append(block)
        cursor = block[-1, 1] + np.array([3.8, 0.0, 0.0])
    return np.concatenate(assembled, axis=0)


def evaluate_method(model: GeoBPE, structures: list[dict], method: str, glue_opt: bool) -> dict:
    rows = []
    for s in structures:
        seg = model.encode(s["coords"])
        pred = reconstruct(s["coords"], seg, glue_opt=glue_opt)
        rows.append(
            {
                "name": s["name"],
                "residues": int(len(s["coords"])),
                "tokens": int(len(seg)),
                "rmsd": rmsd(s["coords"], pred),
                "lddt": ca_lddt(s["coords"], pred),
            }
        )
    return {"method": method, "vocab_size": len(model.vocab), "structures": rows}


def residue_baseline(train: list[dict], test: list[dict], residue_k: int, seed: int) -> dict:
    model = GeoBPE(residue_k=residue_k, pair_k=1, bins=16, iterations=0, seed=seed)
    model.fit(train)
    return evaluate_method(model, test, "residue_quantized_baseline", glue_opt=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/pdb_smoke")
    parser.add_argument("--output-dir", default="checkpoints/geobpe_scaled")
    parser.add_argument("--train-limit", type=int, default=12)
    parser.add_argument("--test-split", default="cameo")
    parser.add_argument("--residue-k", type=int, default=16)
    parser.add_argument("--pair-k", type=int, default=3)
    parser.add_argument("--bins", type=int, default=24)
    parser.add_argument("--iterations", type=int, default=45)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    train = load_split(args.data_root, "train", args.train_limit)
    test = load_split(args.data_root, args.test_split)
    model = GeoBPE(args.residue_k, args.pair_k, args.bins, args.iterations, args.seed)
    model.fit(train)
    output = {
        "config": vars(args),
        "methods": {
            "residue_quantized_baseline": residue_baseline(train, test, args.residue_k, args.seed),
            "geobpe_scaled": evaluate_method(model, test, "geobpe_scaled", glue_opt=True),
            "geobpe_no_glue_opt": evaluate_method(model, test, "geobpe_no_glue_opt", glue_opt=False),
        },
    }
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["methods"], indent=2))


if __name__ == "__main__":
    main()
