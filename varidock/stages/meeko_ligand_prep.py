from dataclasses import dataclass
from pathlib import Path

from varidock.pipeline.types import PDB, PDBQT, Ligand, LigandPrepInput
from varidock.pipeline.stage import Stage
from varidock.broker.meeko import prepare_ligand


@dataclass
class MeekoLigandPrepConfig:
    output_dir: Path
    protonate: bool = True
    pH: float = 7.4


class MeekoLigandPrep(Stage[LigandPrepInput, LigandPrepInput]):
    name = "meeko_ligand_prep"
    input_type = LigandPrepInput
    output_type = LigandPrepInput

    def __init__(self, config: MeekoLigandPrepConfig):
        self.config = config

    def run(self, input: LigandPrepInput) -> LigandPrepInput    :
        output_path = self.config.output_dir / f"{input.ligand.pdb.path.stem}.pdbqt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        prepare_ligand(
            ligand_file=str(input.ligand.pdb.path),
            output_file=str(output_path),
            protonate=self.config.protonate,
            pH=self.config.pH,
        )

        return LigandPrepInput(
            ligand=Ligand(
                name=input.ligand.name,
                pdb=input.ligand.pdb,
                pdbqt=PDBQT(path=output_path)
            ),
            pocket_center=input.pocket_center,
            conf_index=input.conf_index,
            pose_index=input.pose_index,
        )


# MeekoLigandPrepConfig(output_dir=Path("./"))
# ligand = PDB(path=Path(
#     "/spruce/tank/Duncan/IMPACTS2022/SmallMolecules/pdbfiles/917.pdb"
#     ))
# MeekoLigandPrep(MeekoLigandPrepConfig(output_dir=Path("./"))).run(ligand)
