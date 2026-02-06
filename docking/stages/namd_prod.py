# stages/namd_production.py
from dataclasses import dataclass
import subprocess

from docking.pipeline.types import NAMDCheckpoint, Trajectory
from docking.pipeline.stage import Stage
from docking.execution.utils import run_with_interrupt
from docking.execution.slurm import _sbatch

@dataclass
class NAMDProductionConfig:
    local_command: list[str] | None = None
    output_file: str | None = None  # e.g. "run.log"


class NAMDProduction(Stage[NAMDCheckpoint, Trajectory]):
    """Run run.namd N times - production MD."""

    name = "namd_production"
    input_type = NAMDCheckpoint
    output_type = Trajectory
    default_execution = "slurm"

    def __init__(self, config: NAMDProductionConfig):
        self.config = config

    def run_local(self, input: NAMDCheckpoint) -> Trajectory:
        """Run run.namd once locally (for debugging)."""
        if self.config.local_command is None:
            raise ValueError("local_command required for local execution")

        if self.config.output_file:
            with open(input.path / self.config.output_file, "w") as f:
                run_with_interrupt(
                    [*self.config.local_command, "run.namd"],
                    cwd=input.path,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                )
        else:
            run_with_interrupt([*self.config.local_command, "run.namd"], cwd=input.path)

        coor_files = sorted(input.path.glob("run*.coor"))
        return Trajectory(psf=input.path / "system.psf", coor_files=coor_files)

    def submit(
        self, input: NAMDCheckpoint, depends_on: int | None = None
    ) -> Trajectory:
        """Submit run.sh to SLURM."""
        dep = depends_on if depends_on is not None else input.job_id
        job_id = _sbatch(input.path / "run.sh", dep)

        return Trajectory(psf=input.path / "system.psf", coor_files=[], job_id=job_id)

    def run(self, input: NAMDCheckpoint) -> Trajectory:
        return self.run_local(input)
