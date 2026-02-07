# stages/namd_eq2.py
from dataclasses import dataclass
import subprocess

from varidock.pipeline.types import NAMDCheckpoint
from varidock.pipeline.stage import Stage
from varidock.execution.utils import run_with_interrupt
from varidock.execution.slurm import _sbatch

@dataclass
class NAMDEq2Config:
    local_command: list[str] | None = None
    output_file: str | None = None  # e.g. "eq.log"


class NAMDEq2(Stage[NAMDCheckpoint, NAMDCheckpoint]):
    """Run eq2.namd - equilibration with partial restraints (high confidence only)."""

    name = "namd_eq2"
    input_type = NAMDCheckpoint
    output_type = NAMDCheckpoint
    default_execution = "slurm"

    def __init__(self, config: NAMDEq2Config):
        self.config = config

    def run_local(self, input: NAMDCheckpoint) -> NAMDCheckpoint:
        if self.config.local_command is None:
            raise ValueError("local_command required for local execution")

        if self.config.output_file:
            with open(input.path / self.config.output_file, "w") as f:
                run_with_interrupt(
                    [*self.config.local_command, "eq2.namd"],
                    cwd=input.path,
                    stdout=f,
                    stderr=subprocess.STDOUT,  # combine stderr into stdout
                )
        else:
            run_with_interrupt([*self.config.local_command, "eq2.namd"], cwd=input.path)

        return NAMDCheckpoint(path=input.path, restart_prefix="eq2")

    def submit(
        self, input: NAMDCheckpoint, depends_on: int | None = None
    ) -> NAMDCheckpoint:
        """Submit eq2.sh to SLURM, return job ID."""

        dep = depends_on if depends_on is not None else input.job_id
        job_id = _sbatch(input.path / "eq2.sh", dep)
        return NAMDCheckpoint(path=input.path, restart_prefix="eq2", job_id=job_id)

    def run(self, input: NAMDCheckpoint) -> NAMDCheckpoint:
            """Default to local execution for now."""
            return self.run_local(input)
    