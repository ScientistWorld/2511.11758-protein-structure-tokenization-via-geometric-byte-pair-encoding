from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def kabsch_align(p: Any, q: Any) -> Any:
    import numpy as np

    p0 = p - p.mean(axis=0, keepdims=True)
    q0 = q - q.mean(axis=0, keepdims=True)
    u, _, vt = np.linalg.svd(q0.T @ p0)
    r = u @ vt
    if np.linalg.det(r) < 0:
        u[:, -1] *= -1
        r = u @ vt
    return q0 @ r + p.mean(axis=0, keepdims=True)


def rmsd(p: Any, q: Any) -> float:
    import numpy as np

    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    n = min(len(p), len(q))
    pa = p[:n].reshape(-1, 3)
    qa = q[:n].reshape(-1, 3)
    aligned = kabsch_align(pa, qa)
    return float(np.sqrt(np.mean(np.sum((pa - aligned) ** 2, axis=1))))


def ca_lddt(p: Any, q: Any, cutoff: float = 15.0) -> float:
    """Small dependency-free CA lDDT approximation."""
    import numpy as np

    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    n = min(len(p), len(q))
    if p.ndim == 2:
        p = p.reshape(-1, 3, 3)
    if q.ndim == 2:
        q = q.reshape(-1, 3, 3)
    pc = p[:n, 1, :]
    qc = q[:n, 1, :]
    if n < 2:
        return 0.0
    dp = np.linalg.norm(pc[:, None, :] - pc[None, :, :], axis=-1)
    dq = np.linalg.norm(qc[:, None, :] - qc[None, :, :], axis=-1)
    mask = (dp < cutoff) & (dp > 1e-8)
    if not np.any(mask):
        return 0.0
    diff = np.abs(dp - dq)
    scores = (
        (diff < 0.5).astype(float)
        + (diff < 1.0).astype(float)
        + (diff < 2.0).astype(float)
        + (diff < 4.0).astype(float)
    ) / 4.0
    return float(scores[mask].mean())


def summarize_artifact(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text())
    results = {}
    for method, payload in data["methods"].items():
        rows = payload["structures"]
        total_res = sum(row["residues"] for row in rows)
        total_tokens = sum(row["tokens"] for row in rows)
        vocab_size = max(payload["vocab_size"], 2)
        results[method] = {
            "bpr": float(total_tokens * math.log2(vocab_size) / max(total_res, 1)),
            "vocab_size": float(payload["vocab_size"]),
        }
        has_quality = payload.get("include_quality_metrics", False) or all(
            "rmsd" in row and "lddt" in row for row in rows
        )
        has_coords = all(
            "original_coords" in row and "reconstructed_coords" in row for row in rows
        )
        if has_coords:
            results[method]["rmsd"] = sum(
                rmsd(row["original_coords"], row["reconstructed_coords"]) for row in rows
            ) / max(len(rows), 1)
            results[method]["lddt"] = sum(
                ca_lddt(row["original_coords"], row["reconstructed_coords"]) for row in rows
            ) / max(len(rows), 1)
        elif has_quality:
            results[method]["rmsd"] = sum(float(row["rmsd"]) for row in rows) / max(len(rows), 1)
            results[method]["lddt"] = sum(float(row["lddt"]) for row in rows) / max(len(rows), 1)
    return results
