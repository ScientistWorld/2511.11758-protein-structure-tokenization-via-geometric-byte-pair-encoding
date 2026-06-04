from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _flatten_points(coords: Any) -> list[list[float]]:
    if hasattr(coords, "tolist"):
        coords = coords.tolist()
    points: list[list[float]] = []

    def visit(value: Any) -> None:
        if isinstance(value, (list, tuple)):
            if len(value) == 3 and all(isinstance(x, (int, float)) for x in value):
                points.append([float(value[0]), float(value[1]), float(value[2])])
            else:
                for item in value:
                    visit(item)

    visit(coords)
    return points


def _centroid(points: list[list[float]]) -> list[float]:
    n = max(len(points), 1)
    return [sum(point[i] for point in points) / n for i in range(3)]


def _largest_eigenvector_4x4(matrix: list[list[float]]) -> list[float]:
    vec = [1.0, 0.0, 0.0, 0.0]
    for _ in range(80):
        nxt = [sum(matrix[i][j] * vec[j] for j in range(4)) for i in range(4)]
        norm = math.sqrt(sum(x * x for x in nxt))
        if norm < 1e-12:
            break
        vec = [x / norm for x in nxt]
    return vec


def _quat_to_rotation(quat: list[float]) -> list[list[float]]:
    w, x, y, z = quat
    return [
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ]


def _rmsd_pure(p: Any, q: Any) -> float:
    p_points = _flatten_points(p)
    q_points = _flatten_points(q)
    n = min(len(p_points), len(q_points))
    if n == 0:
        return 0.0
    p_points = p_points[:n]
    q_points = q_points[:n]
    pc = _centroid(p_points)
    qc = _centroid(q_points)
    p0 = [[point[i] - pc[i] for i in range(3)] for point in p_points]
    q0 = [[point[i] - qc[i] for i in range(3)] for point in q_points]

    h = [[0.0] * 3 for _ in range(3)]
    for qa, pa in zip(q0, p0):
        for i in range(3):
            for j in range(3):
                h[i][j] += qa[i] * pa[j]

    hxx, hxy, hxz = h[0]
    hyx, hyy, hyz = h[1]
    hzx, hzy, hzz = h[2]
    horn = [
        [hxx + hyy + hzz, hyz - hzy, hzx - hxz, hxy - hyx],
        [hyz - hzy, hxx - hyy - hzz, hxy + hyx, hzx + hxz],
        [hzx - hxz, hxy + hyx, -hxx + hyy - hzz, hyz + hzy],
        [hxy - hyx, hzx + hxz, hyz + hzy, -hxx - hyy + hzz],
    ]
    rot = _quat_to_rotation(_largest_eigenvector_4x4(horn))

    sq = 0.0
    for pa, qa in zip(p0, q0):
        aligned = [sum(rot[i][j] * qa[j] for j in range(3)) for i in range(3)]
        sq += sum((pa[i] - aligned[i]) ** 2 for i in range(3))
    return math.sqrt(sq / n)


def _ca_points(coords: Any) -> list[list[float]]:
    if hasattr(coords, "tolist"):
        coords = coords.tolist()
    if not isinstance(coords, list):
        return []
    if coords and isinstance(coords[0], list) and len(coords[0]) == 3:
        if coords[0] and isinstance(coords[0][0], list):
            return [[float(x) for x in residue[1]] for residue in coords if len(residue) > 1]
        return [[float(x) for x in coords[i + 1]] for i in range(0, len(coords) - 1, 3)]
    return []


def _ca_lddt_pure(p: Any, q: Any, cutoff: float = 15.0) -> float:
    pc = _ca_points(p)
    qc = _ca_points(q)
    n = min(len(pc), len(qc))
    if n < 2:
        return 0.0
    total = 0.0
    count = 0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            dp = math.sqrt(sum((pc[i][k] - pc[j][k]) ** 2 for k in range(3)))
            if not (1e-8 < dp < cutoff):
                continue
            dq = math.sqrt(sum((qc[i][k] - qc[j][k]) ** 2 for k in range(3)))
            diff = abs(dp - dq)
            total += (
                float(diff < 0.5)
                + float(diff < 1.0)
                + float(diff < 2.0)
                + float(diff < 4.0)
            ) / 4.0
            count += 1
    return total / count if count else 0.0


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
    try:
        import numpy as np
    except ModuleNotFoundError:
        return _rmsd_pure(p, q)

    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    n = min(len(p), len(q))
    pa = p[:n].reshape(-1, 3)
    qa = q[:n].reshape(-1, 3)
    aligned = kabsch_align(pa, qa)
    return float(np.sqrt(np.mean(np.sum((pa - aligned) ** 2, axis=1))))


def ca_lddt(p: Any, q: Any, cutoff: float = 15.0) -> float:
    """Small dependency-free CA lDDT approximation."""
    try:
        import numpy as np
    except ModuleNotFoundError:
        return _ca_lddt_pure(p, q, cutoff=cutoff)

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


def summarize_methods(methods: dict) -> dict:
    results = {}
    for method, payload in methods.items():
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
            raise ValueError(
                f"{method} advertises reconstruction quality metrics but is missing "
                "original_coords/reconstructed_coords for at least one structure"
            )
    return results


def summarize_artifact(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text())
    if "experiments" in data:
        return {
            experiment: summarize_methods(payload["methods"])
            for experiment, payload in data["experiments"].items()
        }
    return {"scaled_pdb_tokenization_cameo": summarize_methods(data["methods"])}
