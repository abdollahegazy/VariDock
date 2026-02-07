from pathlib import Path

from openbabel import openbabel as ob
from meeko import MoleculePreparation
from meeko import PDBQTWriterLegacy
from rdkit import Chem


def prepare_ligand(
    ligand_file: str,
    output_file: str,
    protonate: bool = True,
    pH: float = 7.4,
):
    """Protonate (optionally) and convert a ligand file to PDBQT."""
    ext = Path(ligand_file).suffix.lower()
    output_dir = Path(output_file).parent

    if protonate:
        conv = ob.OBConversion()
        conv.SetInAndOutFormats(ext[1:], ext[1:])
        obmol = ob.OBMol()
        conv.ReadFile(obmol, ligand_file)
        obmol.AddHydrogens(False, True, pH)

        # write protonated file for RDKit to read
        protonated_file = str(output_dir / f"{Path(ligand_file).stem}_protonated{ext}")
        conv.WriteFile(obmol, protonated_file)
        ligand_file = protonated_file

    if ext == ".mol2":
        mol = Chem.MolFromMol2File(ligand_file, removeHs=False)
    elif ext in (".sdf", ".sd"):
        mol = Chem.MolFromMolFile(ligand_file, removeHs=False)
    elif ext == ".pdb":
        mol = Chem.MolFromPDBFile(ligand_file, removeHs=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    if mol is None:
        raise RuntimeError(f"RDKit failed to load {ligand_file}")

    mk_prep = MoleculePreparation()
    molsetup_list = mk_prep(mol)
    pdbqt_string = PDBQTWriterLegacy.write_string(molsetup_list[0])[0]
    
    with open(output_file, "w") as f:
        f.write(pdbqt_string)
