from __future__ import annotations

from pathlib import Path

import numpy as np


def load_backbone_pdb(path: str | Path, chain_id: str | None = None) -> np.ndarray:
    """Load N, CA, C backbone atoms from one PDB model as (residues, 3, 3)."""
    residues: dict[tuple[str, int, str], dict[str, np.ndarray]] = {}
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if not line.startswith(("ATOM  ", "HETATM")):
                continue
            atom = line[12:16].strip()
            if atom not in {"N", "CA", "C"}:
                continue
            chain = line[21].strip() or "_"
            if chain_id is not None and chain != chain_id:
                continue
            try:
                resseq = int(line[22:26])
                xyz = np.array(
                    [float(line[30:38]), float(line[38:46]), float(line[46:54])],
                    dtype=np.float64,
                )
            except ValueError:
                continue
            key = (chain, resseq, line[26].strip())
            residues.setdefault(key, {})[atom] = xyz

    coords = []
    for key in sorted(residues):
        atom_map = residues[key]
        if all(atom in atom_map for atom in ("N", "CA", "C")):
            coords.append([atom_map["N"], atom_map["CA"], atom_map["C"]])
    if len(coords) < 4:
        raise ValueError(f"{path} has fewer than four complete backbone residues")
    return np.asarray(coords, dtype=np.float64)


def load_split(root: str | Path, split: str, limit: int | None = None) -> list[dict]:
    files = sorted((Path(root) / split).glob("*.pdb"))
    if limit is not None:
        files = files[:limit]
    structures = []
    for pdb in files:
        coords = load_backbone_pdb(pdb)
        structures.append({"name": pdb.stem, "coords": coords})
    return structures
