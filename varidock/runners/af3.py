from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
import os

from varidock.io import build_af3_input_json
from varidock.jobs import PredictionJob
from varidock.plans import RunPlan
from varidock.runners.base import StructurePredictionRunner

@dataclass(frozen=True)
class AF3Config:
    sif_path: Path
    model_dir: Path
    db_dir: Path
    runner_script: Path

    python_entrypoint: str = "python"

    # Inside-container mount points
    container_input_dir: str = "/root/af_input"
    container_output_dir: str = "/root/af_output"
    container_model_dir: str = "/root/models"
    container_db_dir: str = "/root/public_databases"
    container_runner_dir: str = "/root/runner"

    singularity_args: Sequence[str] = ("--nv",)
    script_args: Sequence[str] = ()

    # @classmethod
    # def from_env(cls) -> "AF3Config":
    #     return cls(
    #         sif_path=Path(os.environ["AF3_SIF_PATH"]),
    #         model_dir=Path(os.environ["AF3_MODEL_DIR"]),
    #         db_dir=Path(os.environ["AF3_DB_DIR"]),
    #         runner_script=Path(os.environ["AF3_RUNNER_SCRIPT"]),
    #     )
    @classmethod
    def from_config(cls, **overrides) -> "AF3Config":
        from varidock.config import VaridockConfig
        cfg = VaridockConfig.load()
        af3 = cfg.af3
        return cls(
            sif_path=overrides.get("sif_path", af3.sif_path),
            model_dir=overrides.get("model_dir", af3.model_dir),
            db_dir=overrides.get("db_dir", af3.db_dir),
            runner_script=overrides.get("runner_script", af3.runner_script),
        )

class AF3Runner(StructurePredictionRunner):
    name = "af3"

    def __init__(self, cfg: AF3Config, seed: int = 1):
        self.cfg = cfg

    
    def plan(self, job: PredictionJob) -> RunPlan:
        input_dir = job.output_dir / "af_input"
        output_dir = job.output_dir / "af_output"

        json_host_path = input_dir / f"{job.name}.json"
        json_container_path = f"{self.cfg.container_input_dir}/{job.name}.json"

        script_path = self.cfg.runner_script.resolve()
        if not script_path.exists():
            raise FileNotFoundError(f"Runner script not found: {script_path}")

        script_host_dir = script_path.parent
        script_name = script_path.name
        script_container_path = f"{self.cfg.container_runner_dir}/{script_name}"

        if not job.input_json_path:
            af3_json = build_af3_input_json(job)
        else:
            af3_json = job.input_json_path.read_text()

        files_text = {
            json_host_path: af3_json,
            output_dir / ".keep": "",  # ensure output dir exists
            input_dir / ".keep": "",  # ensure input dir exists
        }

        argv = ["singularity", "exec"]
        argv += list(self.cfg.singularity_args)

        argv += [
            "--bind",
            f"{input_dir}:{self.cfg.container_input_dir}",
            "--bind",
            f"{output_dir}:{self.cfg.container_output_dir}",
            "--bind",
            f"{self.cfg.model_dir}:{self.cfg.container_model_dir}",
            "--bind",
            f"{self.cfg.db_dir}:{self.cfg.container_db_dir}",
            "--bind",
            f"{script_host_dir}:{self.cfg.container_runner_dir}",
            str(self.cfg.sif_path),
            self.cfg.python_entrypoint,
            script_container_path,
            f"--json_path={json_container_path}",
            f"--model_dir={self.cfg.container_model_dir}",
            f"--db_dir={self.cfg.container_db_dir}",
            f"--output_dir={self.cfg.container_output_dir}",
        ]
        argv += list(self.cfg.script_args)

        files_text[input_dir / "singularity_log.sh"] = "\n".join(argv)
        expected_outputs = [output_dir 
        / job.name.lower()
        / f"{job.name.lower()}_model.cif"] # at least one output

        return RunPlan(
            work_dir=job.output_dir,
            files_text=files_text,
            argv=argv,
            expected_outputs=expected_outputs,
            env=None,
        )