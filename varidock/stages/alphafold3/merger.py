import json
from typing import Sequence
from dataclasses import dataclass
from pathlib import Path

from varidock.types import (
    Ligand,
    AF3MSAOutput, 
    AF3MergedInput
)


@dataclass
class AF3MSAMergerConfig:
    """Configuration for merging monomer MSAs into a multimer input.

    Attributes:
        output_dir (Path): Directory to write merged JSON files.
        seed (int): Random seed for AF3 inference.

    """

    output_dir: Path
    seed: int = 42


class AF3MSAMerger:
    """Merge pre-computed monomer MSA outputs into a multimer input JSON.

    Copies unpairedMsa, pairedMsa, and templates from each monomer's
    data JSON into a single multimer input JSON, with an optional ligand.
    Supports any number of chains (dimers, trimers, etc.).
    Note that the monomer JSONs must have unique chain IDs that do not conflict with each other or the ligand.

    Attributes:
        config (AF3MSAMergerConfig): Output directory and seed configuration.

    """

    name = "af3_msa_merger"

    def __init__(self, config: AF3MSAMergerConfig):
        self.config = config

    def run(
        self,
        msa_outputs: Sequence[AF3MSAOutput],
        ligands: Sequence[Ligand] | None = None,
        name: str | None = None,
    ) -> AF3MergedInput:
        """Merge monomer MSA JSONs into a single multimer input JSON.

        Args:
            msa_outputs (Sequence[AF3MSAOutput]): Pre-computed monomer MSA outputs,
                one per chain. Must not have conflicting chain IDs.
            ligands (Sequence[Ligand] | None): Optional ligands to include in the complex. Must only have SMILES or CCD, not both, and a unique AF3 sequence ID that does not conflict with all other chain IDs.
            name (str | None): Job name. If None, auto-generated from protein IDs
                and ligand name. Like "protein1_protein2_ligand1_ligand2". Should be unique across runs.

        Returns:
            AF3MergedInput: Path to the merged JSON ready for inference.

        Raises:
            ValueError: If no MSA outputs are provided.
            FileNotFoundError: If any monomer data JSON is missing.

        """
        if not msa_outputs:
            raise ValueError("At least one MSA output is required.")

        # Auto-generate name from protein IDs + ligand
        if name is None:
            parts = [m.protein_id.lower() for m in msa_outputs]
            if ligands is not None:
                for ligand in ligands:
                    if ligand.name:
                        parts.append(ligand.name.lower())
            name = "_".join(parts)

        sequences = []
        for msa in msa_outputs:
            if not msa.data_json_path.exists():
                raise FileNotFoundError(f"MSA output not found: {msa.data_json_path}")

            monomer_data = json.loads(msa.data_json_path.read_text())

            # Find the protein entry in the monomer JSON
            protein_entry = None
            for seq in monomer_data["sequences"]:
                if "protein" in seq:
                    protein_entry = seq["protein"]
                    break

            if protein_entry is None:
                raise ValueError(f"No protein entry found in {msa.data_json_path}")

            sequences.append(
                {
                    "protein": {
                        "id": [msa.chain_id],
                        "sequence": protein_entry["sequence"],
                        "modifications": protein_entry.get("modifications", []),
                        "unpairedMsa": protein_entry.get("unpairedMsa"),
                        "pairedMsa": protein_entry.get("pairedMsa"),
                        "templates": protein_entry.get("templates"),
                    }
                }
            )

        if ligands is not None:
            for ligand in ligands:
                if ligand.smiles and ligand.ccd:
                    raise ValueError(f"Ligand {ligand.name} cannot have both SMILES and CCD code.")
                if ligand.af3_sequence_id is None:
                    raise ValueError(f"Ligand {ligand.name} with SMILES or CCD must have an AF3 sequence ID.")

        lig_entry: dict | None = None

        if ligands is not None:
            for ligand in ligands:
                lig_entry = {"id": [ligand.af3_sequence_id]}
                if ligand.smiles:
                    lig_entry["smiles"] = ligand.smiles
                elif ligand.ccd:
                    lig_entry["ccdCodes"] = [ligand.ccd]
                sequences.append({"ligand": lig_entry})

        payload = {
            "name": name,
            "sequences": sequences,
            "modelSeeds": [self.config.seed],
            "dialect": "alphafold3",
            "version": 1,
        }

        out_path = self.config.output_dir / name / f"{name}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2) + "\n")

        return AF3MergedInput(json_path=out_path, name=name)
