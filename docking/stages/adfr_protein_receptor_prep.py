from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import PDB, PDBQT
from docking.pipeline.stage import Stage


@dataclass
class ADFRReceptorPrepConfig:
    conda_env: str
    output_dir: Path
    prepare_receptor_cmd: str = "prepare_receptor4"
    # add more as needed


class ADFRReceptorPrep(Stage[PDB, PDBQT]):
    name = "adfr_receptor_prep"
    input_type = PDB
    output_type = PDBQT

    def __init__(self, config: ADFRReceptorPrepConfig):
        self.config = config

    def run(self, input: PDB) -> PDBQT:
        # 1. Run prepare_receptor4 -r {input.path} -o {output.pdbqt}
        # 2. Return PDBQT
        ...
