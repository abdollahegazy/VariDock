from dataclasses import dataclass
from pathlib import Path
from typing import Tuple,List,Sequence
from varidock.pipeline.types import CIF, ComplexPredictionInput
from varidock.pipeline.stage import Stage
from varidock.runners.af3 import AF3Runner, AF3Config
from varidock.jobs import PredictionJob
from varidock.execution import LocalExecutor

CHAIN_IDS = [chr(i) for i in range(ord("A"), ord("Z") + 1)]

@dataclass
class AF3ComplexPredictorConfig:
    output_dir: Path
    seed: int = 42
    singularity_args: Tuple[str, ...] = ("--nv",)
    script_args: Sequence[str] = ()
    job_name: str | None = None
    chain_ids: List[str] | None = None
    write_only: bool = False 
    overwrite : bool = False

    @classmethod
    def from_config(cls, output_dir: Path) -> "AF3ComplexPredictorConfig":
        return cls(output_dir=output_dir)


class AF3ComplexPredictor(Stage[ComplexPredictionInput, CIF]):
    """
    Predict a multi-chain protein complex with an optional ligand using AF3.
    """

    name = "af3_complex_predictor"
    input_type = ComplexPredictionInput
    output_type = CIF

    def __init__(self, config: AF3ComplexPredictorConfig):
        self.config = config

    def _build_af3_config(self) -> AF3Config:
        base = AF3Config.from_config()
        return AF3Config(
            sif_path=base.sif_path,
            model_dir=base.model_dir,
            db_dir=base.db_dir,
            runner_script=base.runner_script,
            singularity_args=self.config.singularity_args,
            script_args=self.config.script_args,
        )


    def run(self, input: ComplexPredictionInput) -> CIF:
        n = len(input.proteins)
        if n > 26:
            raise ValueError(f"Max 26 chains supported, got {n}")

        chain_ids = self.config.chain_ids or CHAIN_IDS[:n]
        if len(chain_ids) != n:
            raise ValueError(
                f"chain_ids length ({len(chain_ids)}) != protein count ({n})"
            )

        # Job name: explicit > input override > concatenated protein names + lig
        if self.config.job_name:
            job_name = self.config.job_name
        elif input.name:
            job_name = input.name
        else:
            parts = [p.name.replace("/", "_") for p in input.proteins]
            if input.ligand.name:
                parts.append(input.ligand.name)
            job_name = "_".join(parts)

        sequences = [p.sequence for p in input.proteins]

        # Use the first available MSA json, if any
        input_json_path = input.af3_json

        job = PredictionJob(
            name=job_name,
            protein_sequences=sequences,
            protein_chain_ids=chain_ids,
            output_dir=self.config.output_dir,
            input_json_path=input_json_path,
            ligand_smiles=input.ligand.smiles,
            ligand_ccd_code=input.ligand.ccd,
            ligand_id=input.ligand.af3_sequence_id,
            seed=self.config.seed,
        )

        af3_config = self._build_af3_config()
        runner = AF3Runner(af3_config, seed=self.config.seed)
        plan = runner.plan(job)

        executor = LocalExecutor()
        executor.execute(plan, write_only=self.config.write_only, overwrite_inputs=self.config.overwrite)

        cif_path = (
            self.config.output_dir
            / "af_output"
            / job_name.lower()
            / f"{job_name.lower()}_model.cif"
        )

        return CIF(path=cif_path)
