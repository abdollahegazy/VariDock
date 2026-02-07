from dataclasses import dataclass
from pathlib import Path

from varidock.pipeline.types import PDB, PDBQT
from varidock.pipeline.stage import Stage
from varidock.broker.adfr import prepare_receptor


@dataclass
class ADFRReceptorPrepConfig:
    output_dir: Path
    # prepare_receptor params
    repairs: str = ""
    charges_to_add: str | None = "gasteiger"
    preserve_charge_types: str | None = None
    cleanup: str = "nphs_lps_waters_nonstdres"
    delete_single_nonstd_residues: bool = False
    unique_atom_names: bool = False
    verbose: bool = False


class ADFRReceptorPrep(Stage[PDB, PDBQT]):
    name = "adfr_receptor_prep"
    input_type = PDB
    output_type = PDBQT

    def __init__(self, config: ADFRReceptorPrepConfig):
        self.config = config

    def run(self, input: PDB) -> PDBQT:
        output_path = self.config.output_dir / f"{input.path.stem}.pdbqt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        prepare_receptor(
            receptor_filename=str(input.path),
            outputfilename=str(output_path),
            repairs=self.config.repairs,
            charges_to_add=self.config.charges_to_add,
            preserve_charge_types=self.config.preserve_charge_types,
            cleanup=self.config.cleanup,
            delete_single_nonstd_residues=self.config.delete_single_nonstd_residues,
            unique_atom_names=self.config.unique_atom_names,
            verbose=self.config.verbose,
        )

        return PDBQT(path=output_path)

# pdb = PDB(path=Path("../../sandbox/test_proteins/P04757/p04757_model.pdb"), source_cif=Path("../../sandbox/test_proteins/P04757/af_output/p04757/p04757_model.cif"))
# cfg = ADFRReceptorPrepConfig(output_dir=Path("../../sandbox/test_proteins/P04757/"),verbose=True)
# ADFRReceptorPrep(cfg).run(pdb)