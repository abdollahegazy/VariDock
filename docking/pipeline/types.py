from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ProteinSequence:
    sequence: str
    name: str

@dataclass
class CIF:
    path: Path

@dataclass
class PDB:
    path: Path
    #source CIf path (useful if converted from CIF like from AF3)
    source_cif: Path | None = None  

@dataclass
class PDBQT:
    path: Path

@dataclass
class PSF:
    path: Path

@dataclass
class NAMDSimulationDir:
    path: Path  # contains system.psf, system.pdb, system.xsc, eq.namd, etc.

@dataclass
class SLURMPending:
    """Mixin for types that can represent pending SLURM jobs."""
    job_id: int | None = field(default=None, kw_only=True)


@dataclass
class NAMDCheckpoint(SLURMPending):
    path: Path
    restart_prefix: str  # "eq", "eq2", etc.
    
@dataclass
class Trajectory(SLURMPending):
    psf: Path
    pdb: Path
    coor_files: list[Path]


@dataclass
class ConformationSet:
    psf: Path
    pdbs: list[PDB]


@dataclass
class PocketCenter:
    x: float
    y: float
    z: float


@dataclass
class PocketSet:
    conformation: PDB
    centers: list[PocketCenter]


@dataclass
class Ligand:
    path: Path  # mol2 or pdb
    name: str


@dataclass
class DockingResult:
    output_path: Path
    scores: list[float]


# === Composite inputs for multi-input stages ===


@dataclass
class LigandPrepInput:
    ligand: Ligand
    pocket_center: PocketCenter


@dataclass
class DockingInput:
    receptor: PDBQT
    ligand: PDBQT
    pocket_center: PocketCenter
