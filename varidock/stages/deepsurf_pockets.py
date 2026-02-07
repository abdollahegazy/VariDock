from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import PDB, DeepSurfPocketResult
from docking.pipeline.stage import Stage
from docking.broker.deepsurf import predict

@dataclass
class DeepSurfPocketConfig:
    deepsurf_dir: Path  # path to DeepSurf directory
    model_dir: Path
    output_dir: Path
    # DeepSurf params
    model: str = "orig"  # 'orig' or 'lds'
    f: int = 10  # simplification of points mesh
    T: float = 0.9  # ligandability threshold
    batch: int = 32
    voxel_size: float = 1.0
    protonate: bool = False
    expand: bool = False
    discard_points: bool = False
    seed: int | None = None


class DeepSurfPockets(Stage[PDB, DeepSurfPocketResult]):
    name = "deepsurf_pockets"
    input_type = PDB
    output_type = DeepSurfPocketResult

    def __init__(self, config: DeepSurfPocketConfig):
        self.config = config

    def run(self, input: PDB) -> DeepSurfPocketResult:
        # 2. Run predict.py -p {input.path} -mp {model_dir} -o {output_dir}
        # 3. Parse centers.txt
        # 4. Return PocketSet with conformation and list of PocketCenters 

        target_dir = self.config.output_dir / input.path.stem
        centers_file = target_dir / "centers.txt"
    
        predict(
            prot_file=str(input.path),
            model_path=str(self.config.model_dir),
            output=str(self.config.output_dir),
            model=self.config.model,
            f=self.config.f,
            T=self.config.T,
            batch=self.config.batch,
            voxel_size=self.config.voxel_size,
            protonate=self.config.protonate,
            expand=self.config.expand,
            discard_points=self.config.discard_points,
            seed=self.config.seed,
        )

        return DeepSurfPocketResult(
            pocket_dir=target_dir,
            centers_file=centers_file,
            source_pdb=input,
        )

