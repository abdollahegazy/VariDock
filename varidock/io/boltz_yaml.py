from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence, List, Dict

import yaml

from docking.jobs import PredictionJob


def build_boltz_yaml(
    job: PredictionJob,
    msa_paths: Optional[Sequence[Path]] = None,
    version: int = 1,
) -> str:
    if msa_paths is not None and len(msa_paths) != len(job.protein_sequences):
        raise ValueError("msa_paths must match number of proteins")

    sequences: List[Dict[str, Any]] = []

    # Add proteins
    for i, (chain_id, seq) in enumerate(
        zip(job.protein_chain_ids, job.protein_sequences)
    ):
        protein: Dict[str, Any] = {
            "id": chain_id,
            "sequence": seq,
        }
        if msa_paths is not None:
            protein["msa"] = msa_paths[i].as_posix()
        sequences.append({"protein": protein})

    # Add ligand
    if job.ligand_smiles is not None:
        sequences.append(
            {
                "ligand": {
                    "id": job.ligand_id or "L",
                    "smiles": job.ligand_smiles,
                }
            }
        )

    doc: Dict[str, Any] = {
        "version": version,
        "sequences": sequences,
    }

    # Add affinity property if ligand present
    if job.ligand_smiles is not None:
        doc["properties"] = [{"affinity": {"binder": job.ligand_id or "L"}}]

    return yaml.safe_dump(doc, sort_keys=False)
