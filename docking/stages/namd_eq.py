# stages/namd_eq.py
from dataclasses import dataclass
import subprocess

from docking.pipeline.types import NAMDSimulationDir, NAMDCheckpoint
from docking.pipeline.stage import Stage
from docking.execution.utils import run_with_interrupt
from docking.execution.slurm import _sbatch

@dataclass
class NAMDEqConfig:
    local_command: list[str] | None = None
    output_file: str | None = None  # e.g. "eq.log"


class NAMDEq(Stage[NAMDSimulationDir, NAMDCheckpoint]):
    """Run eq.namd - initial equilibration with full restraints."""

    name = "namd_eq"
    input_type = NAMDSimulationDir
    output_type = NAMDCheckpoint
    default_execution = "slurm"

    def __init__(self, config: NAMDEqConfig):
        self.config = config

    # Local (for debugging)
    def run_local(self, input: NAMDSimulationDir) -> NAMDCheckpoint:
        if self.config.local_command is None:
            raise ValueError("local_command required for local execution")

        if self.config.output_file:
            with open(input.path / self.config.output_file, "w") as f:
                run_with_interrupt(
                    [*self.config.local_command, "eq.namd"],
                    cwd=input.path,
                    stdout=f,
                    stderr=subprocess.STDOUT,  # combine stderr into stdout
                )
        else:
            run_with_interrupt([*self.config.local_command, "eq.namd"], cwd=input.path)

        return NAMDCheckpoint(path=input.path, restart_prefix="eq")

        # SLURM
    def submit(
        self, input: NAMDSimulationDir, depends_on: int | None = None
    ) -> NAMDCheckpoint:
        job_id = _sbatch(input.path / "eq.sh", depends_on)
        return NAMDCheckpoint(path=input.path, restart_prefix="eq", job_id=job_id)

    def run(self, input: NAMDSimulationDir) -> NAMDCheckpoint:
            """Default to local execution for now."""
            return self.run_local(input)
