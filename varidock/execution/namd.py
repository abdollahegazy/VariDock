# varidock/execution/namd.py

from pathlib import Path
from typing import Tuple

def get_namd_ns(log_file: Path, timestep_fs: float = 2.0) -> Tuple[float, bool] | None:
    """Parse a NAMD log file and return the simulation progress in nanoseconds."""
    if not log_file.exists():
        return None

    step = None
    complete = False
    with open(log_file) as f:
        for line in f:
            if "WRITING VELOCITIES TO RESTART FILE AT STEP" in line:
                try:
                    step = int(line.strip().split()[-1])
                    complete = False
                except ValueError:
                    continue  # truncated/corrupted line
            if "WRITING VELOCITIES TO OUTPUT FILE AT STEP" in line:
                try:
                    step = int(line.strip().split()[-1])
                    complete = True
                except ValueError:
                    continue  # truncated/corrupted line
                
    if step is None:
        return None

    return step * timestep_fs * 1e-6,complete


def is_namd_done(log_file: Path, target_ns: float, timestep_fs: float = 2.0) -> bool:
    """Check if a NAMD simulation has completed to the target nanoseconds."""
    result = get_namd_ns(log_file, timestep_fs)
    if result is None:
        return False
    ns, complete = result
    return complete and ns >= target_ns