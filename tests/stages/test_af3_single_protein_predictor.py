# tests/stages/test_af3_single_protein_predictor.py
import pytest
from unittest.mock import patch, MagicMock

from varidock.pipeline.types import ProteinSequence, CIF
from varidock.stages.af3_single_protein_predictor import (
    AF3SingleProteinPredictor,
    AF3SingleProteinPredictorConfig,
)


@pytest.fixture
def mock_af3_env(monkeypatch):
    """Set fake AF3 environment variables."""
    monkeypatch.setenv("AF3_SIF_PATH", "/fake/af3.sif")
    monkeypatch.setenv("AF3_MODEL_DIR", "/fake/models")
    monkeypatch.setenv("AF3_DB_DIR", "/fake/db")
    monkeypatch.setenv("AF3_RUNNER_SCRIPT", "/fake/run.py")


class TestAF3SingleProteinPredictor:
    """Tests for AF3 single protein prediction stage."""

    def test_input_output_types(self):
        """Verify stage has correct input/output types."""
        assert AF3SingleProteinPredictor.input_type == ProteinSequence
        assert AF3SingleProteinPredictor.output_type == CIF
        assert AF3SingleProteinPredictor.name == "af3_single_protein_predictor"

    def test_config_defaults(self, tmp_path):
        """Test default config values."""
        config = AF3SingleProteinPredictorConfig(output_dir=tmp_path)
        assert config.seed == 42
        assert config.output_dir == tmp_path

    @patch("varidock.stages.af3_single_protein_predictor.LocalExecutor")
    @patch("varidock.stages.af3_single_protein_predictor.AF3Runner")
    @patch("varidock.stages.af3_single_protein_predictor.AF3Config.from_config")  # Patch the method directly
    def test_run_calls_runner_and_executor(
        self,
        mock_from_config,  # This is now the from_config method
        mock_runner_cls,
        mock_executor_cls,
        tmp_path,
    ):
        """Verify run() wires up runner and executor correctly."""
        # Setup mocks
        mock_config = MagicMock()
        mock_from_config.return_value = mock_config
        
        mock_runner = MagicMock()
        mock_runner_cls.return_value = mock_runner
        mock_plan = MagicMock()
        mock_runner.plan.return_value = mock_plan

        mock_executor = MagicMock()
        mock_executor_cls.return_value = mock_executor

        # Create expected output file
        output_dir = tmp_path / "output"
        cif_path = output_dir / "af_output" / "test_protein" / "test_protein_model.cif"
        cif_path.parent.mkdir(parents=True)
        cif_path.write_text("fake cif content")

        # Run stage
        config = AF3SingleProteinPredictorConfig(output_dir=output_dir)
        stage = AF3SingleProteinPredictor(config)
        input_seq = ProteinSequence(sequence="MANSK", name="test_protein")

        result = stage.run(input_seq)

        # Verify calls
        mock_from_config.assert_called_once()
        mock_runner_cls.assert_called_once()
        mock_executor.execute.assert_called_once_with(mock_plan)

        # Verify result
        assert isinstance(result, CIF)
        assert result.path == cif_path

    @patch("varidock.stages.af3_single_protein_predictor.LocalExecutor")
    @patch("varidock.stages.af3_single_protein_predictor.AF3Runner")
    @patch("varidock.stages.af3_single_protein_predictor.AF3Config")
    def test_run_creates_correct_job(
        self,
        mock_config_cls,
        mock_runner_cls,
        mock_executor_cls,
        mock_af3_env,
        tmp_path,
    ):
        """Verify PredictionJob is created with correct values."""
        # Setup
        mock_config_cls.from_config.return_value = MagicMock()
        mock_runner = MagicMock()
        mock_runner_cls.return_value = mock_runner
        mock_executor_cls.return_value = MagicMock()

        output_dir = tmp_path / "output"
        cif_path = output_dir / "af_output" / "myprotein" / "myprotein_model.cif"
        cif_path.parent.mkdir(parents=True)
        cif_path.write_text("fake")

        config = AF3SingleProteinPredictorConfig(output_dir=output_dir, seed=123)
        stage = AF3SingleProteinPredictor(config)

        stage.run(ProteinSequence(sequence="ACDEF", name="myprotein"))

        # Check the job passed to runner.plan()
        job = mock_runner.plan.call_args[0][0]
        assert job.name == "myprotein"
        assert job.protein_sequences == ["ACDEF"]
        assert job.protein_chain_ids == ["A"]
        assert job.output_dir == output_dir

