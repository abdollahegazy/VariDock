from pathlib import Path

from typing import Protocol,Sequence,Optional

class AF3PredictionProtocol(Protocol):
    job_name: str
    seed: int = 42
    protein_sequences: Sequence[str]
    protein_chain_ids: Sequence[str]
    ligand_smiles: Optional[str]
    ligand_id: Optional[str]
    msa_paths: Optional[Sequence[Path]]  # if AF3 JSON consumes this
