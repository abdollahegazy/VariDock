from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import ProteinSequence, PDB
from docking.pipeline.stage import Stage


from docking.prediction.runners.af3 import AF3Runner, AF3Config
from docking.prediction.jobs import PredictionJob
from docking.prediction.execution import LocalExecutor

@dataclass
class AF3StructureConfig:
    sif_path: Path
    model_dir: Path
    db_dir: Path
    output_dir: Path


class AF3Structure(Stage[ProteinSequence, PDB]):
    name = "af3_structure"
    input_type = ProteinSequence
    output_type = PDB

    def __init__(self, config: AF3StructureConfig):
        self.config = config

    def run(self, input: ProteinSequence) -> PDB: 
        ...
