from pathlib import Path

from docking.plans import RunPlan
from docking.execution import LocalExecutor


def test_local_executor_materialize_run_validate(tmp_path: Path):
    work = tmp_path / "work"
    in_file = work / "input.json"
    out_file = work / "done.txt"

    plan = RunPlan(
        work_dir=work,
        files_text={in_file: '{"ok": true}\n'},
        argv=[
            "python",
            "-c",
            "from pathlib import Path; Path('done.txt').write_text('hi')",
        ],
        expected_outputs=[out_file],
        env=None,
    )

    ex = LocalExecutor()
    ex.execute(plan)

    assert in_file.exists()
    assert out_file.exists()
