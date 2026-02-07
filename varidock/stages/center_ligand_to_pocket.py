from dataclasses import dataclass
from pathlib import Path
import numpy as np


from docking.pipeline.types import PDB, LigandPrepInput
from docking.pipeline.stage import Stage


@dataclass
class CenterLigandConfig:
    output_dir: Path


class CenterLigand(Stage[LigandPrepInput, PDB]):
    name = "ligand_placement"
    input_type = LigandPrepInput
    output_type = PDB

    def __init__(self, config: CenterLigandConfig):
        self.config = config

    def place_ligand(
        self,
        ligand_file: str,
        output_file: str,
        center: tuple[float, float, float],
    ):
        """Translate a ligand PDB so its center of mass sits at the given coordinate.

        Replicates the VMD behavior:
            $a moveby [vecsub {bx by bz} [measure center $a]]
        """
        lines = []
        coords = []

        with open(ligand_file) as f:
            for line in f:
                lines.append(line)
                if line.startswith(("ATOM", "HETATM")):
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    coords.append([x, y, z])

        coords = np.array(coords)
        centroid = coords.mean(axis=0)
        shift = np.array(center) - centroid

        atom_idx = 0
        with open(output_file, "w") as f:
            for line in lines:
                if line.startswith(("ATOM", "HETATM")):
                    new_coords = coords[atom_idx] + shift
                    line = (
                        line[:30]
                        + f"{new_coords[0]:8.3f}{new_coords[1]:8.3f}{new_coords[2]:8.3f}"
                        + line[54:]
                    )
                    atom_idx += 1
                f.write(line)


    def run(self, input: LigandPrepInput) -> PDB:
        center = input.pocket_center
        ligand = input.ligand

        output_path = (
            self.config.output_dir
            / f"ligand_c{input.conf_index}_p{input.pose_index}.pdb"
        )

        self._place_ligand(
            ligand_file=str(ligand.path),
            output_file=str(output_path),
            center=(center.x, center.y, center.z),
        )

        return PDB(path=output_path)