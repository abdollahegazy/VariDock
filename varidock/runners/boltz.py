# runners/boltz.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from varidock.io.af3_load import extract_msas_from_af3_output
from varidock.io.boltz_yaml import build_boltz_yaml
from varidock.jobs import PredictionJob
from varidock.plans import RunPlan
from varidock.runners.base import StructurePredictionRunner


@dataclass(frozen=True)
class BoltzConfig:
    accelerator: str = "gpu"
    extra_args: Sequence[str] = ()


class BoltzRunner(StructurePredictionRunner):
    name = "boltz"

    def __init__(self, cfg: BoltzConfig):
        self.cfg = cfg

    def plan(self, job: PredictionJob) -> RunPlan:
        input_dir = job.output_dir / "boltz_input"
        output_dir = job.output_dir / "boltz_output"

        # Resolve MSA paths
        if job.af3_output_dir is not None:
            msas = extract_msas_from_af3_output(job.af3_output_dir)
            msa_paths = []
            for chain_id in job.protein_chain_ids:
                if chain_id not in msas:
                    raise ValueError(f"No MSA found for chain {chain_id} in AF3 output")
                msa_paths.append(input_dir / f"{chain_id}_unpaired.a3m")
        elif job.msa_paths is not None:
            msas = None
            msa_paths = list(job.msa_paths)
        else:
            raise ValueError("BoltzRunner requires either af3_output_dir or msa_paths")

        # Build files to write
        files_text = {}

        # Write MSA files if extracting from AF3
        if msas is not None:
            for chain_id, msa_path in zip(job.protein_chain_ids, msa_paths):
                files_text[msa_path] = msas[chain_id].unpaired

        # Build YAML
        yaml_path = input_dir / f"{job.name}.yaml"
        files_text[yaml_path] = build_boltz_yaml(job, msa_paths)

        # Build command
        argv = [
            "boltz",
            "predict",
            str(yaml_path),
            "--accelerator",
            self.cfg.accelerator,
            "--out_dir",
            str(output_dir),
        ]
        argv += list(self.cfg.extra_args)

        env = {"PYTORCH_CUDA_ALLOC_CONF": "max_split_size_mb:64"}

        expected_outputs = [
            output_dir
            / f"boltz_results_{job.name}"
            / "predictions" 
            / f"{job.name}" 
            / f"affinity_{job.name}.json"
        ]

        return RunPlan(
            work_dir=job.output_dir,
            files_text=files_text,
            argv=argv,
            expected_outputs=expected_outputs,
            env=env,
        )
