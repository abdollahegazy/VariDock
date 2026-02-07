import os

from MolKit import Read
from AutoDockTools.MoleculePreparation import AD4ReceptorPreparation


def prepare_receptor(
    receptor_filename: str,
    verbose: bool = False,
    outputfilename: str | None = None,
    repairs: str = "",
    charges_to_add: str | None = "gasteiger",
    preserve_charge_types: str | None = None,
    cleanup: str = "nphs_lps_waters_nonstdres",
    mode: str = "automatic",
    delete_single_nonstd_residues: bool = False,
    dictionary: str | None = None,
    unique_atom_names: bool = False,
):
    """Prepare a receptor PDB/MOL2 file for AutoDock4 docking (produces PDBQT)."""
    if not receptor_filename:
        raise ValueError("receptor filename must be specified.")

    mols = Read(receptor_filename)
    if verbose:
        print("read ", receptor_filename)
    mol = mols[0]

    if unique_atom_names:
        for at in mol.allAtoms:
            if mol.allAtoms.get(at.name) > 1:
                at.name = at.name + str(at._uniqIndex + 1)
        if verbose:
            print(
                "renamed %d atoms: each newname is the original name of the atom plus its (1-based) uniqIndex"
                % len(mol.allAtoms)
            )

    preserved = {}
    has_autodock_element = False
    if charges_to_add and preserve_charge_types:
        if hasattr(mol, "allAtoms") and not hasattr(
            mol.allAtoms[0], "autodock_element"
        ):
            file_name, file_ext = os.path.splitext(receptor_filename)
            if file_ext == ".pdbqt":
                has_autodock_element = True
        if preserve_charge_types and not has_autodock_element:
            raise RuntimeError(
                "input format does not have autodock_element SO unable to preserve charges on "
                + preserve_charge_types
            )
        preserved_types = preserve_charge_types.split(",")
        if verbose:
            print("preserved_types=", preserved_types)
        for t in preserved_types:
            if verbose:
                print("preserving charges on type->", t)
            if not len(t):
                continue
            ats = mol.allAtoms.get(lambda x: x.autodock_element == t)
            if verbose:
                print("preserving charges on ", ats.name)
            for a in ats:
                if a.chargeSet is not None:
                    preserved[a] = [a.chargeSet, a.charge]

    if len(mols) > 1:
        if verbose:
            print("more than one molecule in file")
        ctr = 1
        for m in mols[1:]:
            ctr += 1
            if len(m.allAtoms) > len(mol.allAtoms):
                mol = m
                if verbose:
                    print(
                        "mol set to ",
                        ctr,
                        "th molecule with",
                        len(mol.allAtoms),
                        "atoms",
                    )

    mol.buildBondsByDistance()
    alt_loc_ats = mol.allAtoms.get(lambda x: "@" in x.name)
    len_alt_loc_ats = len(alt_loc_ats)
    if len_alt_loc_ats:
        print(
            "WARNING!",
            mol.name,
            "has",
            len_alt_loc_ats,
            " alternate location atoms!\nUse prepare_pdb_split_alt_confs.py to create pdb files containing a single conformation.\n",
        )

    if verbose:
        print("setting up RPO with mode=", mode, end=" ")
        print("and outputfilename= ", outputfilename)
        print("charges_to_add=", charges_to_add)
        print("delete_single_nonstd_residues=", delete_single_nonstd_residues)

    RPO = AD4ReceptorPreparation(  # noqa: F841
        mol,
        mode,
        repairs,
        charges_to_add,
        cleanup,
        outputfilename=outputfilename,
        preserved=preserved,
        delete_single_nonstd_residues=delete_single_nonstd_residues,
        dict=dictionary,
    )

    if charges_to_add:
        for atom, chargeList in list(preserved.items()):
            atom._charges[chargeList[0]] = chargeList[1]
            atom.chargeSet = chargeList[0]
