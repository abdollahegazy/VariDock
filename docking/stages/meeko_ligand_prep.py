from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import LigandPrepInput, PDBQT
from docking.pipeline.stage import Stage


@dataclass
class MeekoLigandPrepConfig:
    conda_env: str
    output_dir: Path
    pH: float = 7.4
    # add more as needed


class MeekoLigandPrep(Stage[LigandPrepInput, PDBQT]):
    name = "meeko_ligand_prep"
    input_type = LigandPrepInput
    output_type = PDBQT

    def __init__(self, config: MeekoLigandPrepConfig):
        self.config = config

    def run(self, input: LigandPrepInput) -> PDBQT:
        # 1. VMD: move ligand to pocket center
        # 2. Write positioned ligand PDB
        # 3. Run mk_prepare_ligand.py -i {ligand.pdb} --pH {pH} -o {output.pdbqt}
        # 4. Return PDBQT
        ...
