# varidock/execution/namd.py

from pathlib import Path


def get_namd_ns(log_file: Path, timestep_fs: float = 2.0) -> float | None:
    """Parse a NAMD log file and return the simulation progress in nanoseconds."""
    if not log_file.exists():
        return None

    step = None
    with open(log_file) as f:
        for line in f:
            if "WRITING VELOCITIES TO RESTART FILE AT STEP" in line:
                step = int(line.strip().split()[-1])
            if "WRITING VELOCITIES TO OUTPUT FILE AT STEP" in line:
                step = int(line.strip().split()[-1])

    if step is None:
        return None

    return step * timestep_fs * 1e-6
