from pathlib import Path
import pytest

from varidock.jobs import PredictionJob


def test_job_valid():
    job = PredictionJob(
        name="x",
        protein_sequences=["AAA", "BBB"],
        protein_chain_ids=["A", "B"],
        output_dir=Path("out"),
    )
    assert job.name == "x"


def test_job_chain_length_mismatch_raises():
    with pytest.raises(ValueError):
        PredictionJob(
            name="x",
            protein_sequences=["AAA", "BBB"],
            protein_chain_ids=["A"],
            output_dir=Path("out"),
        )


def test_job_msa_length_mismatch_raises():
    with pytest.raises(ValueError):
        PredictionJob(
            name="x",
            protein_sequences=["AAA", "BBB"],
            protein_chain_ids=["A", "B"],
            output_dir=Path("out"),
            msa_paths=[Path("a.msa")],
        )
