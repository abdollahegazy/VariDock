# tests/test_af3_load.py
import json
import pytest

from docking.io.af3_load import extract_msas_from_af3_output


@pytest.fixture
def af3_output_dir(tmp_path):
    """Create a minimal AF3 output directory with mock data."""
    data = {
        "dialect": "alphafold3",
        "version": 1,
        "name": "test_job",
        "sequences": [
            {
                "protein": {
                    "id": ["A"],
                    "sequence": "MVLSPADKTN",
                    "unpairedMsa": ">query\nMVLSPADKTN\n>hit1\nMVLSPADKTN\n",
                    "pairedMsa": ">query\nMVLSPADKTN\n",
                }
            },
            {
                "ligand": {
                    "id": ["L"],
                    "smiles": "CCO",
                }
            },
            {
                "protein": {
                    "id": ["B"],
                    "sequence": "GGGGGGGGGG",
                    "unpairedMsa": ">query\nGGGGGGGGGG\n",
                    "pairedMsa": None,
                }
            },
        ],
        "modelSeeds": [1],
    }
    
    (tmp_path / "test_job_data.json").write_text(json.dumps(data))
    return tmp_path


def test_extract_msas_returns_all_proteins(af3_output_dir):
    result = extract_msas_from_af3_output(af3_output_dir)
    
    assert set(result.keys()) == {"A", "B"}


def test_extract_msas_contains_correct_data(af3_output_dir):
    result = extract_msas_from_af3_output(af3_output_dir)
    
    assert result["A"].unpaired == ">query\nMVLSPADKTN\n>hit1\nMVLSPADKTN\n"
    assert result["A"].paired == ">query\nMVLSPADKTN\n"
    assert result["B"].unpaired == ">query\nGGGGGGGGGG\n"
    assert result["B"].paired is None


def test_extract_msas_missing_data_json(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_msas_from_af3_output(tmp_path)