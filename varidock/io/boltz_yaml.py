from pathlib import Path
import yaml


def build_boltz_yaml(
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
