from dataclasses import dataclass
from pathlib import Path

from varidock.pipeline.types import ProteinSequence, CIF
from varidock.pipeline.stage import Stage
from varidock.runners.af3 import AF3Runner, AF3Config
from varidock.jobs import PredictionJob
from varidock.execution import LocalExecutor

@dataclass
class AF3SingleProteinPredictorConfig:
    output_dir: Path
    seed: int = 42
    singularity_args: tuple[str, ...] = ("--nv",)
    script_args: tuple[str, ...] = ()    
    job_name: str | None = None 


    @classmethod
    def from_env(cls, output_dir: Path) -> "AF3SingleProteinPredictorConfig":
        return cls(output_dir=output_dir)


class AF3SingleProteinPredictor(Stage[ProteinSequence, CIF]):
    name = "af3_single_protein_predictor"
    input_type = ProteinSequence
    output_type = CIF

    def __init__(self, config: AF3SingleProteinPredictorConfig):
        self.config = config

    def run(self, input: ProteinSequence) -> CIF:
        af3_config = AF3Config.from_env()
        af3_config = AF3Config(
            sif_path=af3_config.sif_path,
            model_dir=af3_config.model_dir,
            db_dir=af3_config.db_dir,
            runner_script=af3_config.runner_script,
            singularity_args=self.config.singularity_args,
            script_args=self.config.script_args,
        )

        job_name = self.config.job_name or input.name.replace("/", "_")

        job = PredictionJob(
            name=job_name,
            protein_sequences=[input.sequence],
            protein_chain_ids=["A"],
            output_dir=self.config.output_dir,
            input_json_path=input.af3_msa_json_path,
            seed=self.config.seed,
        )

        runner = AF3Runner(af3_config, seed=self.config.seed)
        plan = runner.plan(job)

        executor = LocalExecutor()
        executor.execute(plan)

        cif_path = (
            self.config.output_dir
            / "af_output"
            / input.name.lower()
            / f"{input.name.lower()}_model.cif"
        )

        return CIF(path=cif_path)