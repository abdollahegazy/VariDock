from pathlib import Path
import yaml

from varidock.io.boltz_yaml import build_boltz_yaml
from varidock.jobs import PredictionJob


def test_build_boltz_yaml_minimal(tmp_path):
    job = PredictionJob(
        name="test",
        protein_sequences=["MKTAA"],
        protein_chain_ids=["A"],
        output_dir=tmp_path,
        ligand_smiles="CCO",
        ligand_id="B",
    )

    yml = build_boltz_yaml(job)
    doc = yaml.safe_load(yml)

    assert doc["version"] == 1
    assert len(doc["sequences"]) == 2

    assert doc["sequences"][0]["protein"]["id"] == "A"
    assert doc["sequences"][0]["protein"]["sequence"] == "MKTAA"
    assert "msa" not in doc["sequences"][0]["protein"]

    assert doc["sequences"][1]["ligand"]["id"] == "B"
    assert doc["sequences"][1]["ligand"]["smiles"] == "CCO"


def test_build_boltz_yaml_with_msa(tmp_path):
    job = PredictionJob(
        name="test",
        protein_sequences=["MKTAA"],
        protein_chain_ids=["A"],
        output_dir=tmp_path,
        ligand_smiles="O=C(O)Cc1c[nH]c2ccccc12",
        ligand_id="B",
    )

    yml = build_boltz_yaml(job, msa_paths=[Path("../unpaired_msa.a3m")])
    doc = yaml.safe_load(yml)

    assert doc["sequences"][0]["protein"]["msa"] == "../unpaired_msa.a3m"
    assert doc["properties"] == [{"affinity": {"binder": "B"}}]


def test_build_boltz_yaml_multi_protein(tmp_path):
    job = PredictionJob(
        name="test",
        protein_sequences=["MKTAA", "GGGGG"],
        protein_chain_ids=["A", "B"],
        output_dir=tmp_path,
        ligand_smiles="CCO",
        ligand_id="L",
    )

    yml = build_boltz_yaml(job, msa_paths=[Path("a.a3m"), Path("b.a3m")])
    doc = yaml.safe_load(yml)

    assert len(doc["sequences"]) == 3
    assert doc["sequences"][0]["protein"]["id"] == "A"
    assert doc["sequences"][0]["protein"]["msa"] == "a.a3m"
    assert doc["sequences"][1]["protein"]["id"] == "B"
    assert doc["sequences"][1]["protein"]["msa"] == "b.a3m"
    assert doc["sequences"][2]["ligand"]["id"] == "L"
