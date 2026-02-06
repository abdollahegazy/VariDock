from pathlib import Path
import pytest

from docking.jobs import PredictionJob


def test_from_fasta_files_reads_sequence(tmp_path: Path):
    H = tmp_path / "H.fasta"
    L = tmp_path / "L.fasta"
    H.write_text(">H\nAAAA\n")
    L.write_text(">L\nBBBB\n")

    job = PredictionJob.from_fasta_files(
        name="x",
        fasta_paths=[H, L],
        protein_chain_ids=["H", "L"],
        output_dir=tmp_path / "out",
    )

    assert list(job.protein_sequences) == ["AAAA", "BBBB"]
    assert list(job.protein_chain_ids) == ["H", "L"]


def test_from_fasta_files_empty_raises(tmp_path: Path):
    f = tmp_path / "bad.fasta"
    f.write_text(">x\n\n")
    with pytest.raises(ValueError):
        PredictionJob.from_fasta_files(
            name="x",
            fasta_paths=[f],
            protein_chain_ids=["A"],
            output_dir=tmp_path / "out",
        )
