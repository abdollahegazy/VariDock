from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from varidock.plans import RunPlan

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

    partition: str = "general"
    time: str = "04:00:00"
    cpus: int = 8
    mem: str = "64G"
    gpus: int = 0
    gpu_type: str | None = None
    modules: Sequence[str] = ()
    extra_sbatch: Sequence[str] = ()
    account : str | None = None


class SlurmExecutor:
    """Execute a RunPlan by submitting a SLURM batch job.

    Attributes:
        config (SlurmConfig): SLURM resource configuration.

    """

    def __init__(self, config: SlurmConfig):
        self.config = config

    def execute(
        self,
        plan: "RunPlan",
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
        # Write plan files (input JSONs, .keep dirs, etc.)
        for path, content in plan.files_text.items():
            if overwrite_inputs or not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)

        script_path = plan.work_dir / "submit.sh"
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

    def _build_script(self, plan: "RunPlan") -> str:
        """Build the SLURM batch script content.

        Args:
            plan (RunPlan): Execution plan to generate script for.

        Returns:
            str: Complete SLURM batch script as a string.

        """
        cfg = self.config
        lines = [
            "#!/bin/bash --login",
            f"#SBATCH --job-name={plan.work_dir.name}",
            f"#SBATCH --output={plan.work_dir / 'slurm-%j.out'}",
            f"#SBATCH --error={plan.work_dir / 'slurm-%j.err'}",
            f"#SBATCH --partition={cfg.partition}",
            f"#SBATCH --time={cfg.time}",
            f"#SBATCH --cpus-per-task={cfg.cpus}",
            f"#SBATCH --mem={cfg.mem}",
            f"#SBATCH --account={cfg.account}" if hasattr(cfg, "account") else "",
        ]

        if cfg.gpus > 0:
            gpu_str = f"{cfg.gpu_type}:{cfg.gpus}" if cfg.gpu_type else str(cfg.gpus)
            lines.append(f"#SBATCH --gres=gpu:{gpu_str}")

        for extra in cfg.extra_sbatch:
            lines.append(f"#SBATCH {extra}")

        lines.append("")

        for mod in cfg.modules:
            lines.append(f"module load {mod}")

        if cfg.modules:
            lines.append("")

        if plan.env:
            for k, v in plan.env.items():
                lines.append(f"export {k}={v}")
            lines.append("")

        lines.append(" \\\n    ".join(plan.argv))
        lines.append("")

        return "\n".join(lines)
