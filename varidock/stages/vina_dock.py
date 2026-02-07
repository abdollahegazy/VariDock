from dataclasses import dataclass
from pathlib import Path

from varidock.pipeline.types import DockingInput, DockingResult
from varidock.pipeline.stage import Stage
from varidock.broker.vina import dock


@dataclass
class VinaDockingConfig:
    output_dir: Path
    box_size: tuple[float, float, float] = (20.0, 20.0, 20.0)
    exhaustiveness: int = 32
    write_n_poses: int = 5
    dock_n_poses: int = 20
    scoring_function: str = "vina"
    write_minimized: bool = True


class VinaDocking(Stage[DockingInput, DockingResult]):
    name = "vina_docking"
    input_type = DockingInput
    output_type = DockingResult

    def __init__(self, config: VinaDockingConfig):
        self.config = config
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
    def run(self, input: DockingInput) -> DockingResult:
        center = input.pocket_center
        prefix = f"c{input.conf_index}_p{input.pose_index}"

        output_poses = self.config.output_dir / f"out_poses_{prefix}.pdbqt"
        output_log = self.config.output_dir / f"out_{prefix}.log"
        output_minimize = (
            self.config.output_dir / f"out_minimize_{prefix}.pdbqt"
            if self.config.write_minimized
            else None
        )
        output_poses = self.config.output_dir / f"out_poses_{prefix}.pdbqt"
        output_minimize = (
            self.config.output_dir / f"out_minimize_{prefix}.pdbqt"
            if self.config.write_minimized
            else None
        )


        affinities = dock(
            receptor_pdbqt=str(input.receptor.path),
            ligand_pdbqt=str(input.ligand.path),
            center=(center.x, center.y, center.z),
            output_log=str(output_log),
            output_poses=str(output_poses),
            output_minimize=str(output_minimize) if output_minimize else None,
            box_size=self.config.box_size,
            exhaustiveness=self.config.exhaustiveness,
            write_n_poses=self.config.write_n_poses,
            dock_n_poses=self.config.dock_n_poses,
            scoring_function=self.config.scoring_function,
        )

        return DockingResult(
            output_path=output_poses,
            scores=affinities,
        )

# from varidock.pipeline.types import PDBQT, PocketCenter
# from pathlib import Path

# inp = DockingInput(
#     receptor=PDBQT(
#         path=Path(
#             "/serviceberry/tank/abdolla/SMBA/vina_pipeline_af3_proteins/05docking/Arabidopsis/a0a1i9lq90/protein_conf2.pdbqt"
#         )
#     ),
#     ligand=PDBQT(
#         path=Path(
#             "/serviceberry/tank/abdolla/SMBA/vina_pipeline_af3_proteins/05docking/Arabidopsis/a0a1i9lq90/514/ligand_conf2_pose0.pdbqt"
#         )
#     ),
#     pocket_center=PocketCenter(x=3.255, y=-13.652, z=3.466),
#     conf_index=2,
#     pose_index=0,
# )
# vina_dock = VinaDocking(config=VinaDockingConfig(output_dir=Path("./")))
# result = vina_dock.run(input=inp)
# print(result)


# VinaDocking.run()
# from vina import Vina

# v = Vina(sf_name="vina")
# v.set_receptor("/tank/abdolla/docking/Arabidopsis/a0a1i9lq90/protein_conf2.pdbqt")
# v.set_ligand_from_file(
#     "/tank/abdolla/docking/Arabidopsis/a0a1i9lq90/514/ligand_conf2_pose0.pdbqt"
# )
# v.compute_vina_maps(center=[3.255, -13.652, 3.466], box_size=[20, 20, 20])

# # Score the current pose
# energy = v.score()
# print("Score before minimization: %.3f (kcal/mol)" % energy[0])

# # Minimized locally the current pose
# energy_minimized = v.optimize()
# print("Score after minimization : %.3f (kcal/mol)" % energy_minimized[0])

# v.write_pose(
#     "/tank/abdolla/docking/Arabidopsis/a0a1i9lq90/514/out_minimize_c2_p0.pdbqt",
#     overwrite=True,
# )

# # Dock the ligand
# v.dock(exhaustiveness=32, n_poses=20)
# v.write_poses(
#     "/tank/abdolla/docking/Arabidopsis/a0a1i9lq90/514/out_poses_c2_p0.pdbqt",
#     n_poses=5,
#     overwrite=True,
# )
