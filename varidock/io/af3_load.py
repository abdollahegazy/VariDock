from __future__ import annotations

import json
from pathlib import Path
from varidock.structure import MSAData


def extract_msas_from_af3_output(af3_output_dir: Path) -> dict[str, MSAData]:
    """Extract MSA data for all proteins in an AF3 output directory.

    Returns: {chain_id: MSAData}
    """
    af3_output_dir = Path(af3_output_dir)

    data_files = sorted(af3_output_dir.glob("*_data.json"))
    if not data_files:
        raise FileNotFoundError(f"No *_data.json found in {af3_output_dir}")

    data = json.loads(data_files[0].read_text())

    result = {}
    for seq in data.get("sequences", []):
        protein = seq.get("protein")
        if protein is None:
            continue

        chain_id = protein.get("id")
        if isinstance(chain_id, list):
            chain_id = chain_id[0]  # AF3 uses ["A"] format

        result[chain_id] = MSAData(
            paired=protein.get("pairedMsa"),
            unpaired=protein.get("unpairedMsa"),
        )

    return result