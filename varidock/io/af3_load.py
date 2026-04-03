"""Loads MSA data from AlphaFold 3 output directories. The main function, `extract_msas_from_af3_output`, takes a path to an AF3 output directory, searches for the expected JSON files containing the MSA data, and extracts this information into a dictionary mapping chain IDs to `MSAData` objects. This allows users to easily access the paired and unpaired MSA data for each protein chain predicted by AF3, facilitating downstream analysis or integration with other tools in the Varidock pipeline."""
# varidock/io/af3_load.py
from __future__ import annotations

import json
from pathlib import Path
from varidock.types import MSAData


def extract_msas_from_af3_output(data_json: Path) -> tuple[MSAData, str] | None:
    """
    Extract MSA data and protein sequence from an AF3 output JSON file.
    Note, this currently expects single protein JSONs with a single sequence within them.

    Returns:
        Tuple of (MSAData, sequence) or None if no protein found.
    """

    if not data_json.exists():
        raise FileNotFoundError(f"No *_data.json found in {data_json}")

    data = json.loads(data_json.read_text())

    for seq in data.get("sequences", []):
        protein = seq.get("protein")
        if protein is None:
            continue

        msa = MSAData(
            paired=protein.get("pairedMsa"),
            unpaired=protein.get("unpairedMsa"),
        )
        return msa, protein.get("sequence", "")

    return None