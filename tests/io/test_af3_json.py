from pathlib import Path
import json

from docking.jobs import PredictionJob
from docking.io.af3_json import _build_af3_input_json


def test_build_af3_input_json_shape_single_job():
    job = PredictionJob(
        name="4UIN",
        protein_sequences=["EVQL", "DIQM"],
        protein_chain_ids=["H", "L"],
        ligand_smiles="C=C",
        ligand_id="L",
        output_dir=Path("out"),
        seed=69
    )

    s = _build_af3_input_json(job)
    payload = json.loads(s)

    assert payload["name"] == "4UIN"
    assert payload["dialect"] == "alphafold3"
    assert payload["version"] == 1
    assert payload["modelSeeds"] == [69]
    assert len(payload["sequences"]) == 3
    assert payload["sequences"][0]["protein"]["id"] == ["H"]
    assert payload["sequences"][0]["protein"]["sequence"] == "EVQL"
    assert payload["sequences"][1]["protein"]["id"] == ["L"]
    assert payload["sequences"][1]["protein"]["sequence"] == "DIQM"
    assert payload["sequences"][2]["ligand"]["id"] == ["L"]
    assert payload["sequences"][2]["ligand"]["smiles"] == "C=C"