from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import PDB, PDBQT
from docking.pipeline.stage import Stage
from docking.broker.meeko import prepare_ligand


@dataclass
class MeekoLigandPrepConfig:
    output_dir: Path
    protonate: bool = True
    pH: float = 7.4


class MeekoLigandPrep(Stage[PDB, PDBQT]):
    name = "meeko_ligand_prep"
    input_type = PDB
    output_type = PDBQT

    def __init__(self, config: MeekoLigandPrepConfig):
        self.config = config

    def run(self, input: PDB) -> PDBQT:
        output_path = self.config.output_dir / f"{input.path.stem}.pdbqt"

        prepare_ligand(
            ligand_file=str(input.path),
            output_file=str(output_path),
            protonate=self.config.protonate,
            pH=self.config.pH,
        )

        return PDBQT(path=output_path)


MeekoLigandPrepConfig(output_dir=Path("./"))
ligand = PDB(path=Path(
    "/spruce/tank/Duncan/IMPACTS2022/SmallMolecules/pdbfiles/917.pdb"
    ))
MeekoLigandPrep(MeekoLigandPrepConfig(output_dir=Path("./"))).run(ligand)
