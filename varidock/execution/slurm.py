import subprocess
from pathlib import Path

# execution/slurm.py
def _sbatch(script: Path, depends_on: int | None = None) -> int:
    """Submit script to SLURM, return job ID."""
    cmd = ["sbatch", "--parsable"]
    if depends_on:
        cmd += [f"--dependency=afterok:{depends_on}"]
    cmd.append(str(script))
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, cwd=script.parent
    )
    return int(result.stdout.strip())

def get_slurm_queue_count() -> int:
    """Count current user's pending + running jobs.
    """
    result = subprocess.run(
        ["squeue", "--me", "-h", "--format=%i"],
        capture_output=True,
        text=True,
        check=True,
    )
    return len(result.stdout.strip().splitlines())