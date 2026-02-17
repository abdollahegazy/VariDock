"""AF3 runner and plan builder for Singularity execution.

Defines AF3Config for container paths and arguments, and a function to build a RunPlan
for executing AF3 with the specified configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


from varidock.plans import RunPlan

@dataclass(frozen=True)
class AF3Config:
    """Configuration for running AF3 via Singularity.

    Attributes:
        sif_path (Path): Path to the AF3 Singularity image.
        model_dir (Path): Host path to AF3 model parameters.
        db_dir (Path): Host path to genetic databases.
        runner_script (Path): Host path to run_alphafold.py.
        python_entrypoint (str): Python binary inside the container.
        singularity_args (Sequence[str]): Extra args for singularity exec.
        script_args (Sequence[str]): Extra args for run_alphafold.py.
        container_input_dir (str): Container mount point for input JSON.
        container_output_dir (str): Container mount point for AF3 output.
        container_model_dir (str): Container mount point for model parameters.
        container_db_dir (str): Container mount point for genetic databases.
        container_runner_dir (str): Container mount point for run_alphafold.py.

    """

    sif_path: Path
    model_dir: Path
    db_dir: Path
    runner_script: Path

    python_entrypoint: str = "python"
    singularity_args: Sequence[str] = ("--nv",)
    script_args: Sequence[str] = ()

    # Inside-container mount points
    container_input_dir: str = "/root/af_input"
    container_output_dir: str = "/root/af_output"
    container_model_dir: str = "/root/models"
    container_db_dir: str = "/root/public_databases"
    container_runner_dir: str = "/root/runner"


    @classmethod
    def from_config(cls, **overrides) -> "AF3Config":
        """Create an AF3Config instance by loading defaults from VaridockConfig and applying overrides.
        
        :param cls: The AF3Config class itself (automatically passed by @classmethod).
        :param overrides: Keyword arguments to override default configuration values loaded from VaridockConfig.
        :return: An instance of AF3Config with values taken from VaridockConfig and overridden by any provided arguments.
        :rtype: AF3Config
        """
        from varidock.config import VaridockConfig

        cfg = VaridockConfig.load()
        af3 = cfg.af3
        return cls(
            sif_path=overrides.pop("sif_path", af3.sif_path),
            model_dir=overrides.pop("model_dir", af3.model_dir),
            db_dir=overrides.pop("db_dir", af3.db_dir),
            runner_script=overrides.pop("runner_script", af3.runner_script),
            **overrides,
        )
        


def plan_af3(
        cfg: AF3Config,
        name: str,
        input_json: str,
        output_dir: Path
        ) -> RunPlan:
    """Build a RunPlan for a single AF3 execution.

    Args:
        cfg (AF3Config): Singularity and AF3 configuration.
        name (str): Job name (used for file naming).
        input_json (str): AF3 input JSON content as a string.
        output_dir (Path): Root output directory (af_input/ and af_output/ created inside).

    Returns:
        RunPlan: Ready-to-execute plan with argv, files, and expected outputs.

    Raises:
        FileNotFoundError: If the runner script does not exist.

    """
    input_dir = output_dir / "af_input"
    af_output = output_dir / "af_output"

    script_path = cfg.runner_script.resolve()
    if not script_path.exists():
        raise FileNotFoundError(f"AlphaFold runner python script not found: {script_path}")

    files = {
        input_dir / f"{name}.json": input_json,
        input_dir / ".keep": "",
        af_output / ".keep": "",
    }

    binds = {
        input_dir: cfg.container_input_dir,
        af_output: cfg.container_output_dir,
        cfg.model_dir: cfg.container_model_dir,
        cfg.db_dir: cfg.container_db_dir,
        script_path.parent: cfg.container_runner_dir,
    }

    argv = ["singularity", "exec", *cfg.singularity_args]
    for host, container in binds.items():
        argv += ["--bind", f"{Path(host).resolve()}:{container}"]

    argv += [
        str(cfg.sif_path),
        cfg.python_entrypoint,
        f"{cfg.container_runner_dir}/{script_path.name}",
        f"--json_path={cfg.container_input_dir}/{name}.json",
        f"--model_dir={cfg.container_model_dir}",
        f"--db_dir={cfg.container_db_dir}",
        f"--output_dir={cfg.container_output_dir}",
        *cfg.script_args,
    ]

    files[input_dir / "singularity_log.sh"] = " \\\n    ".join(argv)

    # When --norun_inference is set, AF3 only generates MSAs (no CIF output)
    norun_inference = "--norun_inference" in cfg.script_args
    suffix = "_data.json" if norun_inference else "_model.cif"
    expected = [af_output / name / f"{name}{suffix}"]


    return RunPlan(
        work_dir=output_dir,
        files_text=files,
        argv=argv,
        expected_outputs=expected,
        env=None,
    )