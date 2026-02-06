from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import PDB, PocketSet
from docking.pipeline.stage import Stage


@dataclass
class DeepSurfConfig:
    conda_env: str
    predict_script: Path  # path to DeepSurf predict.py
    model_dir: Path
    output_dir: Path
    # add more as needed


class DeepSurfPockets(Stage[PDB, PocketSet]):
    name = "deepsurf_pockets"
    input_type = PDB
    output_type = PocketSet

    def __init__(self, config: DeepSurfConfig):
        self.config = config

    def run(self, input: PDB) -> PocketSet:
        # 1. Activate conda env
        # 2. Run predict.py -p {input.path} -mp {model_dir} -o {output_dir}
        # 3. Parse centers.txt
        # 4. Return PocketSet with conformation and list of PocketCenters
        ...
