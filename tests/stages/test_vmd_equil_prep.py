# tests/stages/test_vmd_equil_prep.py
import pytest
from unittest.mock import patch, MagicMock


from docking.pipeline.types import PDB, NAMDSimulationDir
# from docking.stages.vmd_equil_prep import NAMDEquilPrep, NAMDEquilPrepConfig
from docking.stages.vmd_equil_prep import VMDEquilPrep as NAMDEquilPrep
from docking.stages.vmd_equil_prep import VMDEquilPrepConfig as NAMDEquilPrepConfig
class TestNAMDEquilPrep:
    """Tests for NAMD equilibration prep stage."""

    def test_input_output_types(self):
        """Verify stage has correct input/output types."""
        assert NAMDEquilPrep.input_type == PDB
        assert NAMDEquilPrep.output_type == NAMDSimulationDir
        assert NAMDEquilPrep.name == "vmd_equil_prep"

    @patch("docking.stages.vmd_equil_prep.run_with_interrupt")
    def test_run_generates_tcl_script(self, mock_run, tmp_path):
        """Verify TCL script is generated with correct content."""
        # Setup directories
        toppar_dir = tmp_path / "toppar"
        template_dir = tmp_path / "templates"
        output_dir = tmp_path / "output"
        toppar_dir.mkdir()
        template_dir.mkdir()

        # Create dummy template files
        (toppar_dir / "top_all36_prot.rtf").write_text("dummy topology")
        (template_dir / "eq.namd").write_text("eq config")
        (template_dir / "eq2.namd").write_text("eq2 config")
        (template_dir / "run.namd").write_text("run config")
        (template_dir / "eq.sh").write_text("#!/bin/bash\necho DUMMY_NAME")
        (template_dir / "eq2.sh").write_text("#!/bin/bash\necho DUMMY_NAME")
        (template_dir / "run.sh").write_text("#!/bin/bash\necho DUMMY_NAME")

        # Create input PDB
        input_pdb = tmp_path / "protein.pdb"
        input_pdb.write_text("ATOM dummy content")

        config = NAMDEquilPrepConfig(
            toppar_dir=toppar_dir,
            template_dir=template_dir,
            output_dir=output_dir,
        )
        stage = NAMDEquilPrep(config)
        result = stage.run(PDB(path=input_pdb))

        # Verify TCL script was written
        tcl_path = output_dir / "prep.tcl"
        assert tcl_path.exists()

        tcl_content = tcl_path.read_text()
        assert "package require psfgen" in tcl_content
        assert "package require solvate" in tcl_content
        assert "package require autoionize" in tcl_content
        assert str(input_pdb) in tcl_content
        assert "restrain.pdb" in tcl_content
        assert "restrain2.pdb" in tcl_content

        # Verify VMD was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "vmd"
        assert "-dispdev" in call_args
        assert "text" in call_args

    @patch("docking.stages.vmd_equil_prep.run_with_interrupt")
    def test_run_copies_templates(self, mock_run, tmp_path):
        """Verify template files are copied to output directory."""
        # Setup
        toppar_dir = tmp_path / "toppar"
        template_dir = tmp_path / "templates"
        output_dir = tmp_path / "output"
        toppar_dir.mkdir()
        template_dir.mkdir()

        (toppar_dir / "top_all36_prot.rtf").write_text("topology")
        (toppar_dir / "par_all36m_prot.prm").write_text("params")
        (template_dir / "eq.namd").write_text("eq config")
        (template_dir / "eq2.namd").write_text("eq2 config")
        (template_dir / "run.namd").write_text("run config")
        (template_dir / "eq.sh").write_text("DUMMY_NAME")
        (template_dir / "eq2.sh").write_text("DUMMY_NAME")
        (template_dir / "run.sh").write_text("DUMMY_NAME")

        input_pdb = tmp_path / "myprotein.pdb"
        input_pdb.write_text("ATOM dummy")

        config = NAMDEquilPrepConfig(
            toppar_dir=toppar_dir,
            template_dir=template_dir,
            output_dir=output_dir,
        )
        stage = NAMDEquilPrep(config)
        stage.run(PDB(path=input_pdb))

        # Verify NAMD configs copied
        assert (output_dir / "eq.namd").exists()
        assert (output_dir / "eq2.namd").exists()
        assert (output_dir / "run.namd").exists()

        # Verify toppar copied
        assert (output_dir / "toppar" / "top_all36_prot.rtf").exists()
        assert (output_dir / "toppar" / "par_all36m_prot.prm").exists()

    @patch("docking.stages.vmd_equil_prep.run_with_interrupt")
    def test_run_seds_shell_scripts(self, mock_run, tmp_path):
        """Verify DUMMY_NAME is replaced in shell scripts."""
        # Setup
        toppar_dir = tmp_path / "toppar"
        template_dir = tmp_path / "templates"
        output_dir = tmp_path / "output"
        toppar_dir.mkdir()
        template_dir.mkdir()

        (toppar_dir / "top_all36_prot.rtf").write_text("topology")
        (template_dir / "eq.namd").write_text("eq")
        (template_dir / "eq2.namd").write_text("eq2")
        (template_dir / "run.namd").write_text("run")
        (template_dir / "eq.sh").write_text("#!/bin/bash\nnamd2 DUMMY_NAME.namd")
        (template_dir / "eq2.sh").write_text("#!/bin/bash\nnamd2 DUMMY_NAME.namd")
        (template_dir / "run.sh").write_text("#!/bin/bash\nnamd2 DUMMY_NAME.namd")

        input_pdb = tmp_path / "P09483_model.pdb"
        input_pdb.write_text("ATOM dummy")

        config = NAMDEquilPrepConfig(
            toppar_dir=toppar_dir,
            template_dir=template_dir,
            output_dir=output_dir,
        )
        stage = NAMDEquilPrep(config)
        stage.run(PDB(path=input_pdb))

        # Verify DUMMY_NAME replaced with stem
        eq_sh_content = (output_dir / "eq.sh").read_text()
        assert "DUMMY_NAME" not in eq_sh_content
        assert "P09483_model" in eq_sh_content

    @patch("docking.stages.vmd_equil_prep.run_with_interrupt")
    def test_run_returns_namd_simulation_dir(self, mock_run, tmp_path):
        """Verify correct return type."""
        toppar_dir = tmp_path / "toppar"
        template_dir = tmp_path / "templates"
        output_dir = tmp_path / "output"
        toppar_dir.mkdir()
        template_dir.mkdir()

        (toppar_dir / "top_all36_prot.rtf").write_text("topology")
        (template_dir / "eq.namd").write_text("eq")
        (template_dir / "eq2.namd").write_text("eq2")
        (template_dir / "run.namd").write_text("run")
        (template_dir / "eq.sh").write_text("sh")
        (template_dir / "eq2.sh").write_text("sh")
        (template_dir / "run.sh").write_text("sh")

        input_pdb = tmp_path / "protein.pdb"
        input_pdb.write_text("ATOM dummy")

        config = NAMDEquilPrepConfig(
            toppar_dir=toppar_dir,
            template_dir=template_dir,
            output_dir=output_dir,
        )
        stage = NAMDEquilPrep(config)
        result = stage.run(PDB(path=input_pdb))

        assert isinstance(result, NAMDSimulationDir)
        assert result.path == output_dir
