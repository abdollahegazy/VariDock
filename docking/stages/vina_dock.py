from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import DockingInput, DockingResult
from docking.pipeline.stage import Stage


@dataclass
class VinaDockingConfig:
    conda_env: str
    output_dir: Path
    box_size: tuple[float, float, float] = (20.0, 20.0, 20.0)
    exhaustiveness: int = 32
    n_poses: int = 20
    # add more as needed


class VinaDocking(Stage[DockingInput, DockingResult]):
    name = "vina_docking"
    input_type = DockingInput
    output_type = DockingResult

    def __init__(self, config: VinaDockingConfig):
        self.config = config

    def run(self, input: DockingInput) -> DockingResult:
        # 1. Set receptor and ligand
        # 2. Compute vina maps with pocket center and box size
        # 3. Score and minimize
        # 4. Dock with exhaustiveness and n_poses
        # 5. Write poses
        # 6. Parse scores
        # 7. Return DockingResult
        ...
