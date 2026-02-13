from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from varidock.io.fasta import _read_single_fasta

@dataclass(frozen=True)
class PredictionJob:
    name: str
    protein_sequences: Sequence[str]
    protein_chain_ids: Sequence[str]
    output_dir: Path
    input_json_path: Path | None = None
    ligand_smiles: Optional[str] = None
    ligand_id: Optional[str] = None
    ligand_ccd_code: Optional[str] = None
    msa_paths: Optional[Sequence[Path]] = None
    seed: Optional[int] = 42
    af3_output_dir: Optional[Path] = None

    @classmethod
    def from_fasta_files(
        cls,
        *,
        name: str,
        seed: int =42,
        fasta_paths: Sequence[Path],
        protein_chain_ids: Sequence[str],
        output_dir: Path,
        ligand_smiles: Optional[str] = None,
        ligand_id: Optional[str] = None,
        msa_paths: Optional[Sequence[Path]] = None,
    ) -> "PredictionJob":
        if len(fasta_paths) != len(protein_chain_ids):
            raise ValueError("fasta_paths and protein_chain_ids must have the same length")

        sequences = [_read_single_fasta(Path(p)) for p in fasta_paths]

        return cls(
            name=name,
            protein_sequences=sequences,
            protein_chain_ids=protein_chain_ids,
            output_dir=output_dir,
            ligand_smiles=ligand_smiles,
            ligand_id=ligand_id,
            msa_paths=msa_paths,
            seed=seed,
        )

    def __post_init__(self):
        if len(self.protein_chain_ids) != len(self.protein_sequences):
            raise ValueError("protein_chain_ids and protein_sequences must have the same length")
        if self.msa_paths is not None and len(self.msa_paths) != len(self.protein_sequences):
            raise ValueError("msa_paths must match protein_sequences length (or be None)")
        object.__setattr__(self, "output_dir", self.output_dir.resolve())

        if self.msa_paths is not None and self.af3_output_dir is not None:
            raise ValueError("Cannot set both msa_paths and af3_output_dir. Please provide your own MSA path, or the AF3 output dir to load MSAs from.")
