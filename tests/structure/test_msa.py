# add to tests/test_af3_load.py (or create tests/test_msa.py)
import pytest
from varidock.structure import MSAData


def test_write_unpaired_a3m(tmp_path):
    msa = MSAData(
        unpaired=">query\nMVLSPADKTN\n>hit1\nMVLSPADKTN\n",
        paired=None,
    )

    out_path = tmp_path / "test.a3m"
    msa.write_unpaired_a3m(out_path)

    assert out_path.exists()
    assert out_path.read_text() == ">query\nMVLSPADKTN\n>hit1\nMVLSPADKTN\n"


def test_write_unpaired_a3m_raises_when_none(tmp_path):
    msa = MSAData(unpaired=None, paired=None)

    with pytest.raises(ValueError):
        msa.write_unpaired_a3m(tmp_path / "test.a3m")
