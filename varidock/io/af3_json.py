import json

from pathlib import Path
from typing import Protocol, Sequence, Optional



class AF3PredictionProtocol(Protocol):
    name: str
    seed: int = 42
    protein_sequences: Sequence[str]
    protein_chain_ids: Sequence[str]
    ligand_smiles: Optional[str]
    ligand_ccd_code: Optional[str]
    ligand_id: Optional[str]
    msa_paths: Optional[Sequence[Path]]  # if AF3 JSON consumes this

def build_af3_input_json(job: AF3PredictionProtocol) -> str:
    if len(job.protein_sequences) != len(job.protein_chain_ids):
        raise ValueError("PredictionJob.sequences and chain_ids must have same length")
    if (job.ligand_smiles is not None) == (job.ligand_ccd_code is not None):
        raise ValueError("only one of ligand_smiles or ligand_ccd_code should be provided")
    if job.ligand_id is None:
        raise ValueError("ligand_id is required.")
    
    sequences = []
    for chain_id, seq in zip(job.protein_chain_ids, job.protein_sequences):
        sequences.append(
            {
                "protein": {
                    "id": [chain_id],
                    "sequence": seq,
                }
            }
        )
    if job.ligand_smiles is not None:
            sequences.append(
                {
                    "ligand": {
                        "id": [job.ligand_id],
                        "smiles": job.ligand_smiles,
                    }
                }
            )
    if job.ligand_ccd_code is not None:
            sequences.append(
                {
                    "ligand": {
                        "id": [job.ligand_id],
                        "ccdCodes": [job.ligand_ccd_code],
                    }
                }
            )
    payload = {
        "name": job.name,
        "sequences": sequences,
        "modelSeeds": [job.seed],
        "dialect": "alphafold3",
        "version": 1,
    }

    return json.dumps(payload, indent=2) + "\n"