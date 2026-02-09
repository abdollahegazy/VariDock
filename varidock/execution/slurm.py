import re
import subprocess
from pathlib import Path

# execution/slurm.py
def _sbatch(script: Path, depends_on: int | None = None) -> int:
    """Submit script to SLURM, return job ID."""
    cmd = ["sbatch", "--parsable"]
    if depends_on is not None:
        cmd += [f"--dependency=afterok:{depends_on}"]
    cmd.append(script.name)
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, cwd=script.parent
    )
    return int(result.stdout.strip())

def get_slurm_queue_count() -> int:
    """Count current user's pending + running jobs.
    """
    result = subprocess.run(
        ["squeue", "--me", "-h","-r", "--format=%i"],
        capture_output=True,
        text=True,
        check=True,
    )
    return len(result.stdout.strip().splitlines())


def get_job_name(script: Path) -> str | None:
    with open(script) as f:
        for line in f:
            line = line.strip()
            match = re.match(r"#SBATCH\s+(?:--job-name=|-J\s+)(.+)", line)
            if match:
                return match.group(1).strip()
    return None


def get_running_job_names() -> set[str]:
    result = subprocess.run(
        ["squeue", "--me", "-h", "--format=%j"],
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.strip().splitlines())

def job_exists(script: Path) -> bool:
    job_name = get_job_name(script)
    if not job_name:
        return False
    running_jobs = get_running_job_names()
    return job_name in running_jobs