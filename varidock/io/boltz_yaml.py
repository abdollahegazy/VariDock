from pathlib import Path
from typing import Any, Dict,List
import yaml


def _build_boltz_yaml_single_prot(
    protein_sequence: str,
    protein_chain_id: str,
    msa_path: Path,
    ligand_smiles: str,
    ligand_chain_id: str = "B",
) -> str:
    """Build a Boltz input YAML string."""
    data = {
        "version": 1,
        "sequences": [
            {
                "protein": {
                    "id": protein_chain_id,
                    "sequence": protein_sequence,
                    "msa": str(msa_path),
                }
            },
            {
                "ligand": {
                    "id": ligand_chain_id,
                    "smiles": ligand_smiles,
                }
            },
        ],
        "properties": [
            {"affinity": {"binder": ligand_chain_id}},
        ],
    }

    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def _build_boltz_yaml_multi_prot(
    protein_sequences: List[str],
    protein_chain_ids: List[str],
    msa_path_map: Dict[str, Path],
    ligand:str,
    ccd=False,
    ligand_chain_id: str = "B",
) -> str:
    """Build a Boltz input YAML string."""
    data: Dict[str, Any] = {
        "version": 1,
        "sequences": [],
    }
    
    if ligand_chain_id in protein_chain_ids:
        raise ValueError("Ligand chain ID cannot be the same as any protein chain ID")
    
    if set(protein_chain_ids) != set(msa_path_map.keys()):
        raise ValueError("Protein chain IDs must match keys in MSA path map")
    if len(protein_chain_ids) != len(protein_sequences):
        raise ValueError("Number of protein chain IDs must match number of sequences.")
    if len(set(protein_chain_ids)) != len(protein_chain_ids):
        raise ValueError("Protein chain IDs must be unique.")
    
    for chain_id, sequence in zip(protein_chain_ids, protein_sequences):
        data["sequences"].append(
            {
                "protein": {
                    "id": chain_id,
                    "sequence": sequence,
                    "msa": str(msa_path_map[chain_id]),
                }
            }
        )
    if not ccd:
        data["sequences"].append(
            {
                "ligand": {
                    "id": ligand_chain_id,
                    "smiles": ligand,
                }
            }
        )
    else    :
        data["sequences"].append(
            {
                "ligand": {
                    "id": ligand_chain_id,
                    "ccd": ligand,
                }
            }
        )
    data["properties"] = [
        {"affinity": {"binder": ligand_chain_id}},
    ]

    return yaml.dump(data, default_flow_style=False, sort_keys=False)
