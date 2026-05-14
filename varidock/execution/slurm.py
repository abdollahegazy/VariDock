from __future__ import annotations

from dataclasses import dataclass

from pathlib import Path
from typing import Sequence

from varidock.plans import RunPlan

from varidock.execution.materialize import PlanMaterializer, DefaultMaterializer
# from varidock.execution.run import CommandRunner, LocalCommandRunner, CompletedRun
from varidock.execution.validate import PlanValidator, ExpectedOutputsValidator

@dataclass
class SlurmConfig:
    """SLURM job configuration.

    Attributes:
        partition (str): SLURM partition name.
        time (str): Wall time limit (e.g. '04:00:00').
        cpus (int): Number of CPUs to request.
        mem (str): Memory to request (e.g. '64G').
        gpus (int): Number of GPUs to request.
        gpu_type (str | None): GPU type constraint (e.g. 'a100', 'h200').
        modules (Sequence[str]): Environment modules to load before execution.
        extra_sbatch (Sequence[str]): Additional #SBATCH lines.

    """

    cpus: int
    mem: str 
    gpus: int = 0
    account: str = "vermaaslab"
    time: str = "4:0:0"
    gres_flags: Sequence[str] = ("--gres-flags=enforce-binding",)
    gpu_type: str = ""
    nodes: int = 1
    ntasks_per_node:int = 1
    extra_sbatch: Sequence[str] = ()
    modules: Sequence[str] = ()
    script_name: str = "submit.sh"



# @dataclass
class SlurmExecutor:
    materializer: PlanMaterializer = DefaultMaterializer()
    validator: PlanValidator = ExpectedOutputsValidator()

    def __init__(self, config: SlurmConfig):
        self.config = config

    def execute(
        self,
        plan: RunPlan,
        write_only: bool = False,
        overwrite_inputs: bool = False,
    ) -> Path:
        """Write a SLURM batch script and optionally submit it.

        Args:
            plan (RunPlan): The execution plan with argv, files, and work_dir.
            write_only (bool): If True, write the script but don't submit.
            overwrite_inputs (bool): If True, overwrite existing input files.

        Returns:
            Path: Path to the generated SLURM batch script.

        """

        self.materializer.materialize(plan,overwrite=overwrite_inputs)
        script_path = plan.work_dir / self.config.script_name
        script_path.write_text(self._build_script(plan))
        script_path.chmod(0o755)

        if not write_only:
            import subprocess

            result = subprocess.run(
                ["sbatch", str(script_path)],
                capture_output=True,
                text=True,
                cwd=plan.work_dir,
            )
            if result.returncode != 0:
                raise RuntimeError(f"sbatch failed: {result.stderr}")
            print(result.stdout.strip())

        return script_path

    def _build_script(self,plan:RunPlan,job_name="") -> str:
        """
        Build the SLURM batch script content.
        Args:
            plan (RunPlan): Execution plan to generate script for.
        Returns:
            str: Complete SLURM batch script as a string.
        """
        cfg = self.config
        lines = [
            "#!/bin/bash --login",
            f"#SBATCH --cpus-per-task={cfg.cpus}",
            f"#SBATCH --nodes={cfg.nodes}",
            f"#SBATCH --ntasks-per-node={cfg.ntasks_per_node}",
            f"#SBATCH --mem={cfg.mem}",
            f"#SBATCH --time={cfg.time}",
            f"#SBATCH --account={cfg.account}",
            f"#SBATCH --job-name={job_name}" if job_name else "",
        ]

        if cfg.gpus > 0:
            lines.extend([
            f"#SBATCH -C [{cfg.gpu_type}]",
            f"#SBATCH --gres=gpu:{cfg.gpus}",
            f"#SBATCH --gpus-per-task={cfg.gpus}",
            ])

        for extra in cfg.extra_sbatch:
            lines.append(f"#SBATCH {extra}")

        # for gres_extra in cfg.gres_flags:
        #     lines.append(f"#SBATCH {gres_extra}")

        for mod in cfg.modules:
            lines.append(f"module {mod}")
        
        if plan.env:
            for k, v in plan.env.items():
                lines.append(f"export {k}={v}")
            lines.append("")

        lines.append(" \\\n    ".join(plan.argv))
        # lines.append("")

        # print("\n".join(lines))

        return "\n".join(lines)
