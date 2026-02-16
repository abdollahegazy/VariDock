"""Provides functionality for building input JSON files for AlphaFold 3 structure prediction. The main function, `build_af3_input_json`, takes in the necessary information about the protein sequences, chain IDs, and optional ligand information, and constructs a properly formatted JSON string that can be used as input for AF3. This includes validation of the input parameters to ensure that the generated JSON adheres to the expected schema for AF3 inputs."""

# varidock/io/af3_json.py
import json
from typing import Sequence


def build_af3_input_json(
    name: str,
    sequences: Sequence[str],
    chain_ids: Sequence[str],
    seed: int = 42,
    ligand_smiles: str | None = None,
    ligand_ccd: str | None = None,
    ligand_id: str | None = None,
) -> str:
    """Build an AF3 input JSON string for structure prediction.

    Protein chain IDs are assigned in the order of the provided sequences. 
    If a ligand is included, it must have a unique AF3 sequence ID and either a SMILES string or CCD code.
    
    Args:
        name (str): Job name.
        sequences (Sequence[str]): Protein sequences, one per chain.
        chain_ids (Sequence[str]): Chain identifiers, one per sequence.
        seed (int): Random seed for AF3.
        ligand_smiles (str | None): SMILES string for the ligand.
        ligand_ccd (str | None): CCD code for the ligand.
        ligand_id (str | None): AF3 sequence ID for the ligand (required if ligand provided).

    Returns:
        str: AF3 input JSON as a string.

    Raises:
        ValueError: If sequences/chain_ids mismatch or ligand args are invalid.

    """
    if len(sequences) != len(chain_ids):
        raise ValueError("sequences and chain_ids must have same length")

    if ligand_smiles and ligand_ccd:
        raise ValueError("Only one of ligand_smiles or ligand_ccd allowed")

    has_ligand = ligand_smiles is not None or ligand_ccd is not None
    if has_ligand:
        if ligand_id is None:
            raise ValueError("ligand_id required when ligand is provided")
        assert ligand_id not in chain_ids, "ligand_id must be unique and not conflict with protein chain IDs"

    seq_entries = [
        {"protein": {"id": [cid], "sequence": seq}}
        for cid, seq in zip(chain_ids, sequences)
    ]

    if ligand_id and ligand_smiles is not None:
        seq_entries.append({"ligand": {"id": [ligand_id], "smiles": ligand_smiles}})
    elif ligand_id and ligand_ccd is not None:
        seq_entries.append({"ligand": {"id": [ligand_id], "ccdCodes": [ligand_ccd]}})

    payload = {
        "name": name,
        "sequences": seq_entries,
        "modelSeeds": [seed],
        "dialect": "alphafold3",
        "version": 1,
    }

    return json.dumps(payload, indent=2) + "\n"