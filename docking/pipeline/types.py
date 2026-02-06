from dataclasses import dataclass
from pathlib import Path

@dataclass
class ProteinSequence:
    sequence: str
    name: str

@dataclass
class PDB:
    path: Path

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
class Trajectory:
    psf: Path
    coor_files: list[Path]


@dataclass
class ConformationSet:
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
