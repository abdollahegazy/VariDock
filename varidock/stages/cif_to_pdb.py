from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import CIF, PDB
from docking.pipeline.stage import Stage
from docking.execution.utils import run_with_interrupt


@dataclass
class CIFToPDBConfig:
    """Configuration for CIF to PDB conversion.

    Attributes:
        output_dir: Directory to write PDB file. If None, writes next to input CIF.
    """

    output_dir: Path | None = None


class CIFToPDB(Stage[CIF, PDB]):
    """
    Convert CIF structure file to PDB format using Open Babel.
    """

    name = "cif_to_pdb"
    input_type = CIF
    output_type = PDB

    def __init__(self, config: CIFToPDBConfig | None = None):
        self.config = config or CIFToPDBConfig()

    def run(self, input: CIF) -> PDB:
        if self.config.output_dir:
            pdb_path = self.config.output_dir / f"{input.path.stem}.pdb"
        else:
            pdb_path = input.path.with_suffix(".pdb")

        run_with_interrupt(["obabel", str(input.path), "-O", str(pdb_path)])

        return PDB(path=pdb_path, source_cif=input.path)
