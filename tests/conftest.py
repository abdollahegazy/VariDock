import pytest
from pathlib import Path
import shutil


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_cif(fixtures_dir) -> Path:
    """Return path to sample CIF file."""
    return fixtures_dir / "a0a1i9lq74.cif"


@pytest.fixture
def sample_expected_pdb_from_cif(fixtures_dir) -> Path:
    """Return path to expected PDB output from CIF input."""
    return fixtures_dir / "a0a1i9lq74_from_cif.pdb"

requires_obabel = pytest.mark.skipif(
    shutil.which("obabel") is None, reason="obabel not found"
)

requires_vmd = pytest.mark.skipif(shutil.which("vmd") is None, reason="vmd not found")