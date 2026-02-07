from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import ProteinSequence, CIF
from docking.pipeline.stage import Stage
from docking.runners.af3 import AF3Runner, AF3Config
from docking.jobs import PredictionJob
from docking.execution import LocalExecutor
@dataclass
class AF3SingleProteinPredictorConfig:
    output_dir: Path
    seed: int = 42

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

        job = PredictionJob(
            name=input.name,
            protein_sequences=[input.sequence],
            protein_chain_ids=["A"],
            output_dir=self.config.output_dir,
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