from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import NAMDSimulationDir, Trajectory
from docking.pipeline.stage import Stage


@dataclass
class NAMDEquilConfig:
    namd_executable: Path
    num_runs: int = 11  # run001.coor through run011.coor
    # add more as needed


class NAMDEquil(Stage[NAMDSimulationDir, Trajectory]):
    name = "namd_equil"
    input_type = NAMDSimulationDir
    output_type = Trajectory

    def __init__(self, config: NAMDEquilConfig):
        self.config = config

    def run(self, input: NAMDSimulationDir) -> Trajectory:
        # 1. Run eq.sh (or eq.namd directly)
        # 2. Run eq2.sh
        # 3. Run run.sh (produces run001.coor ... run011.coor)
        # 4. Return Trajectory with psf and coor files
        ...
