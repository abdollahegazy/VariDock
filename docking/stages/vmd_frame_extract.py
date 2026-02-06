from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import Trajectory, ConformationSet
from docking.pipeline.stage import Stage


@dataclass
class VMDFrameExtractionConfig:
    output_dir: Path
    # add more as needed


class VMDFrameExtraction(Stage[Trajectory, ConformationSet]):
    name = "vmd_frame_extraction"
    input_type = Trajectory
    output_type = ConformationSet

    def __init__(self, config: VMDFrameExtractionConfig):
        self.config = config

    def run(self, input: Trajectory) -> ConformationSet:
        # 1. Load PSF
        # 2. Load each .coor file as a frame
        # 3. Select protein atoms
        # 4. Write each frame as PDB
        # 5. Return ConformationSet with list of PDBs
        ...
