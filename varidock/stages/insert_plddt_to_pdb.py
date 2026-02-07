# stages/insert_plddt_from_af3.py
import json
from dataclasses import dataclass
from pathlib import Path

from docking.pipeline.types import PDB
from docking.pipeline.stage import Stage


@dataclass
class InsertPLDDTConfig:
    output_dir: Path | None = None  # if None, overwrite input PDB


class InsertPLDDT(Stage[PDB, PDB]):
    """Insert pLDDT values from AF3 confidences JSON into PDB beta column."""

    name = "insert_plddt"
    input_type = PDB
    output_type = PDB

    def __init__(self, config: InsertPLDDTConfig | None = None):
        self.config = config or InsertPLDDTConfig()

    def run(self, input: PDB) -> PDB:
        if input.source_cif is None:
            raise ValueError("PDB has no source_cif, can't find confidences JSON")

        # Find confidences JSON
        cif_dir = input.source_cif.parent
        jobname = input.source_cif.stem.replace("_model", "")
        confidences_json = cif_dir / f"{jobname}_confidences.json"

        if not confidences_json.exists():
            raise FileNotFoundError(f"Confidences JSON not found: {confidences_json}")

        # Load pLDDT values
        with open(confidences_json) as f:
            data = json.load(f)
        atom_plddts = data["atom_plddts"]

        # Read PDB, inject pLDDT into beta column
        pdb_lines = input.path.read_text().splitlines()
        new_lines = []
        atom_idx = 0

        for line in pdb_lines:
            if line.startswith(("ATOM", "HETATM")):
                if atom_idx < len(atom_plddts):
                    plddt = atom_plddts[atom_idx] / 100.0  # scale to 0-1
                    # Beta column is columns 61-66 in PDB format
                    new_line = f"{line[:60]}{plddt:6.2f}{line[66:]}"
                    new_lines.append(new_line)
                    atom_idx += 1
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # Check atom count matches
        pdb_atom_count = sum(
            1 for line in pdb_lines if line.startswith(("ATOM", "HETATM"))
        )
        if pdb_atom_count != len(atom_plddts):
            raise ValueError(
                f"Atom count mismatch: PDB has {pdb_atom_count} atoms, "
                f"confidences JSON has {len(atom_plddts)}"
            )

        # Write output
        if self.config.output_dir:
            output_path = self.config.output_dir / input.path.name
        else:
            output_path = input.path  # overwrite

        output_path.write_text("\n".join(new_lines) + "\n")

        return PDB(path=output_path, source_cif=input.source_cif)


# pdb = PDB(
#     path=Path(
#         "/serviceberry/tank/abdolla/SMBA/vina_pipeline_af3_proteins/01AF3_Simulations/pdb_converted/Arabidopsis/a0a1i9lq74.pdb"
#     ),
#     source_cif=Path(
#         "/serviceberry/tank/abdolla/SMBA/vina_pipeline_af3_proteins/01AF3_Simulations/output_raw/Arabidopsis/inference/a0a1i9lq74/a0a1i9lq74_model.cif"
#     ),
# )

# stage = InsertPLDDT(InsertPLDDTConfig(Path("./test")))
# output_pdb = stage.run(pdb)
# print(f"Output PDB with pLDDT: {output_pdb.path}")