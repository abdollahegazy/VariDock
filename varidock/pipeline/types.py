from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

@dataclass
class ProteinSequence:
    sequence: str
    name: str
    af3_msa_json_path: Path | None = None  # optional path for the MSA JSON file

@dataclass
class CIF:
    path: Path
    source_sequence: ProteinSequence | None = None


@dataclass
class PDB:
    path: Path
    source_cif: Path | None = None  

@dataclass
class PDBQT:
    path: Path

@dataclass
class PSF:
    path: Path
    source_pdb: PDB | None = None   

@dataclass
class NAMDSimulationDir:
    path: Path  # contains system.psf, system.pdb, system.xsc, eq.namd, etc.
    source_pdb: PDB | None = None


@dataclass
class SLURMPending:
    """Mixin for types that can represent pending SLURM jobs."""

    job_id: int | None = field(default=None, kw_only=True)


@dataclass
class NAMDCheckpoint(SLURMPending):
    path: Path
    restart_prefix: str  # "eq", "eq2", etc.
    source_namd_sim_dir: NAMDSimulationDir | None = None
    

@dataclass
class Trajectory(SLURMPending):
    psf: PSF
    pdb: PDB
    coor_files: Sequence[Path]
    source_checkpoint: NAMDCheckpoint | None = None


@dataclass
class ConformationSet:
    psf: Path
    pdbs: list[PDB]
    source_trajectory: Trajectory | None = None


@dataclass
class PocketCenter:
    x: float
    y: float
    z: float


@dataclass
class PocketSet:
    conformation: PDB
    centers: Sequence[PocketCenter]


@dataclass
class Ligand:
    name: str
    af3_sequence_id : str | None = None  # optional AF3 sequence ID for this ligand
    pdb: PDB | None = None
    pdbqt: PDBQT | None = None
    ccd: str | None = None
    smiles: str | None = None


@dataclass
class DeepSurfPocketResult:
    pocket_dir: Path
    centers_file: Path
    source_pdb: PDB

# === Composite inputs for multi-input stages ===

@dataclass
class LigandPrepInput:
    ligand: Ligand
    pocket_center: PocketCenter
    conf_index: int
    pose_index: int

@dataclass
class DockingInput:
    receptor: PDBQT
    ligand: PDBQT
    pocket_center: PocketCenter
    conf_index: int
    pose_index: int


@dataclass
class DockingResult:
    output_path: Path
    scores: Sequence[float]



@dataclass
class ComplexPredictionInput:
    """
    Input for multi-protein + single ligand structure prediction.
    """

    proteins: Sequence[ProteinSequence]
    ligand: Ligand 
    name: str | None = None  # optional complex name override   
    af3_json : Path | None = None  # optional AF3 input JSON path override
    
    def __post_init__(self):
        if not self.proteins:
            raise ValueError("At least one ProteinSequence is required.")
        if (self.ligand.smiles is None) and (self.ligand.ccd is None):
            raise ValueError("Provide both ligand_smiles and ligand_id, or neither.")
        if self.ligand.af3_sequence_id is None:
            raise ValueError("ligand_id is required.")
        if self.ligand.name is None:
            raise ValueError("ligand name is required.")