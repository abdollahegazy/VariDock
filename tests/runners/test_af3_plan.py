from pathlib import Path

from varidock.jobs import PredictionJob
from varidock.runners.af3 import AF3Runner, AF3Config


def test_af3_plan_has_expected_paths(tmp_path: Path):
    # Make a fake runner script that actually exists
    runner_dir = tmp_path / "runner"
    runner_dir.mkdir()
    
    (runner_dir / "ponderosa_run.py").write_text("# dummy\n")


    job = PredictionJob(
        name="4UIN",
        protein_sequences=["AAAA", "BBBB"],
        protein_chain_ids=["H", "L"],
        output_dir=tmp_path / "job_out",
    )

    cfg = AF3Config(
        sif_path=Path("/fake/af3.sif"),
        model_dir=Path("/fake/models"),
        db_dir=Path("/fake/db"),
        runner_script=runner_dir / "ponderosa_run.py",
    )

    plan = AF3Runner(cfg).plan(job)


    assert (job.output_dir / "af_input" / "4UIN.json") in plan.files_text
    assert plan.argv[0:2] == ["singularity", "exec"]
    assert (job.output_dir / "af_output" / job.name.lower() / f"{job.name.lower()}_model.cif") in plan.expected_outputs