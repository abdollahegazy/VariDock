from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import PDB, NAMDSimulationDir
from docking.pipeline.stage import Stage


@dataclass
class NAMDEquilPrepConfig:
    toppar_dir: Path
    template_dir: Path  # contains eq.namd, eq2.namd, run.namd templates
    output_dir: Path
    # add more as needed


class NAMDEquilPrep(Stage[PDB, NAMDSimulationDir]):
    name = "namd_equil_prep"
    input_type = PDB
    output_type = NAMDSimulationDir

    def __init__(self, config: NAMDEquilPrepConfig):
        self.config = config

    def run(self, input: PDB) -> NAMDSimulationDir:
        # 1. psfgen - build PSF/PDB
        # 2. solvate - add water box
        # 3. autoionize - add ions
        # 4. write system files (psf, pdb, xsc)
        # 5. create restraint files from pLDDT
        # 6. copy NAMD config templates
        ...
