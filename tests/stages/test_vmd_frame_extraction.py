# tests/stages/test_vmd_frame_extraction.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from varidock.pipeline.types import Trajectory, ConformationSet, PDB
from varidock.stages.vmd_frame_extract import (
    VMDFrameExtraction,
    VMDFrameExtractionConfig,
)


class TestVMDFrameExtraction:
    """Tests for VMD frame extraction stage."""

    def test_input_output_types(self):
        """Verify stage has correct input/output types."""
        assert VMDFrameExtraction.input_type == Trajectory
        assert VMDFrameExtraction.output_type == ConformationSet
        assert VMDFrameExtraction.name == "vmd_frame_extraction"

    @patch("varidock.stages.vmd_frame_extract.run_with_interrupt")
    def test_run_generates_tcl_script(self, mock_run, tmp_path):
        """Verify TCL script is generated with correct content."""
        # Setup
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        psf_path = tmp_path / "system.psf"
        pdb_path = tmp_path / "system.pdb"
        psf_path.write_text("dummy psf")
        pdb_path.write_text("dummy pdb")

        coor_files = []
        for i in range(3):
            coor = tmp_path / f"run{i:03d}.coor"
            coor.write_text(f"dummy coor {i}")
            coor_files.append(coor)

        # Create dummy output PDBs (simulating VMD output)
        for i in range(4):  # 3 coors + 1 initial pdb = 4 frames
            (output_dir / f"protein_conf{i}.pdb").write_text(f"frame {i}")
        (output_dir / "protein.psf").write_text("protein psf")

        config = VMDFrameExtractionConfig(output_dir=output_dir)
        stage = VMDFrameExtraction(config)

        trajectory = Trajectory(psf=psf_path, pdb=pdb_path, coor_files=coor_files)
        result = stage.run(trajectory)

        # Verify TCL script was written
        tcl_path = output_dir / "frame_extraction.tcl"
        assert tcl_path.exists()

        tcl_content = tcl_path.read_text()
        assert str(psf_path) in tcl_content
        assert str(pdb_path) in tcl_content
        assert "protein_conf" in tcl_content
        assert "protein.psf" in tcl_content

        # Verify VMD was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "vmd"
        assert "-dispdev" in call_args
        assert "-eofexit" in call_args

    @patch("varidock.stages.vmd_frame_extract.run_with_interrupt")
    def test_run_returns_conformation_set(self, mock_run, tmp_path):
        """Verify correct return type with PDBs."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        psf_path = tmp_path / "system.psf"
        pdb_path = tmp_path / "system.pdb"
        psf_path.write_text("dummy psf")
        pdb_path.write_text("dummy pdb")

        coor_files = [tmp_path / "run001.coor"]
        coor_files[0].write_text("dummy coor")

        # Create dummy outputs
        (output_dir / "protein.psf").write_text("protein psf")
        for i in range(3):
            (output_dir / f"protein_conf{i}.pdb").write_text(f"frame {i}")

        config = VMDFrameExtractionConfig(output_dir=output_dir)
        stage = VMDFrameExtraction(config)

        trajectory = Trajectory(psf=psf_path, pdb=pdb_path, coor_files=coor_files)
        result = stage.run(trajectory)

        assert isinstance(result, ConformationSet)
        assert result.psf == output_dir / "protein.psf"
        assert len(result.pdbs) == 3
        assert all(isinstance(p, PDB) for p in result.pdbs)
        assert result.pdbs[0].path == output_dir / "protein_conf0.pdb"

    @patch("varidock.stages.vmd_frame_extract.run_with_interrupt")
    def test_run_loads_all_coor_files(self, mock_run, tmp_path):
        """Verify all coor files are added to TCL script."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        psf_path = tmp_path / "system.psf"
        pdb_path = tmp_path / "system.pdb"
        psf_path.write_text("dummy psf")
        pdb_path.write_text("dummy pdb")

        coor_files = []
        for i in range(11):
            coor = tmp_path / f"run{i:03d}.coor"
            coor.write_text(f"dummy coor {i}")
            coor_files.append(coor)

        (output_dir / "protein.psf").write_text("psf")

        config = VMDFrameExtractionConfig(output_dir=output_dir)
        stage = VMDFrameExtraction(config)

        trajectory = Trajectory(psf=psf_path, pdb=pdb_path, coor_files=coor_files)
        stage.run(trajectory)

        tcl_content = (output_dir / "frame_extraction.tcl").read_text()
        for coor in coor_files:
            assert str(coor) in tcl_content
