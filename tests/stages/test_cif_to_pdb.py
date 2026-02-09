import shutil
import pytest
from unittest.mock import patch

from varidock.pipeline.types import CIF, PDB
from varidock.stages.cif_to_pdb import CIFToPDB, CIFToPDBConfig


requires_obabel = pytest.mark.skipif(
    shutil.which("obabel") is None, reason="obabel not found"
)


class TestCIFToPDB:
    """Tests for CIF to PDB conversion stage."""

    def test_input_output_types(self):
        """Verify stage has correct input/output types."""
        assert CIFToPDB.input_type == CIF
        assert CIFToPDB.output_type == PDB
        assert CIFToPDB.name == "cif_to_pdb"

    def test_config_defaults(self):
        """Test default config values."""
        config = CIFToPDBConfig()
        assert config.output_dir is None

    def test_config_with_output_dir(self, tmp_path):
        """Test config with explicit output directory."""
        config = CIFToPDBConfig(output_dir=tmp_path)
        assert config.output_dir == tmp_path

    @requires_obabel
    @patch("varidock.stages.cif_to_pdb.run_with_interrupt")
    def test_run_writes_to_same_dir_when_no_output_dir(self, mock_run, tmp_path):
        """When output_dir is None, PDB is written next to input CIF."""
        # Setup
        cif_path = tmp_path / "protein.cif"
        cif_path.write_text("dummy cif content")

        stage = CIFToPDB()
        result = stage.run(CIF(path=cif_path))

        # Verify
        expected_pdb_path = tmp_path / "protein.pdb"
        assert result.path == expected_pdb_path
        mock_run.assert_called_once_with(
            ["obabel", str(cif_path), "-O", str(expected_pdb_path)]
        )

    @requires_obabel
    @patch("varidock.stages.cif_to_pdb.run_with_interrupt")
    def test_run_writes_to_output_dir_when_specified(self, mock_run, tmp_path):
        """When output_dir is set, PDB is written there."""
        # Setup
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        cif_path = input_dir / "protein.cif"
        cif_path.write_text("dummy cif content")

        config = CIFToPDBConfig(output_dir=output_dir)
        stage = CIFToPDB(config)
        result = stage.run(CIF(path=cif_path))

        # Verify
        expected_pdb_path = output_dir / "protein.pdb"
        assert result.path == expected_pdb_path
        mock_run.assert_called_once_with(
            ["obabel", str(cif_path), "-O", str(expected_pdb_path)]
        )

    def test_run_integration(self, sample_cif, sample_expected_pdb_from_cif, tmp_path):
        """Integration test with real obabel conversion."""
        pytest.importorskip("subprocess")

        if not sample_cif.exists():
            pytest.skip("Sample CIF fixture not found")

        config = CIFToPDBConfig(output_dir=tmp_path)
        stage = CIFToPDB(config)
        result = stage.run(CIF(path=sample_cif))

        assert result.path.exists()
        assert result.path.suffix == ".pdb"

        if sample_expected_pdb_from_cif.exists():
            actual = result.path.read_text()
            expected = sample_expected_pdb_from_cif.read_text()

            # Strip version lines
            actual_lines = [
                line for line in actual.splitlines() if not line.startswith("AUTHOR")
            ]
            expected_lines = [
                line for line in expected.splitlines() if not line.startswith("AUTHOR")
            ]

            assert actual_lines == expected_lines
