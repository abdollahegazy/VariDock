from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence, Optional


@dataclass(frozen=True)
class RunPlan:
    """
    Declarative description of a system-level run.

    The executor is responsible for:
    - writing files
    - executing argv
    - verifying expected outputs
    """

    # Where the run logically happens
    work_dir: Path

    # Files that must exist before execution
    files_text: Mapping[Path, str]

    # Command to execute (already tokenized)
    argv: Sequence[str]

    # Files whose existence implies success
    expected_outputs: Sequence[Path]

    # Optional environment variables
    env: Optional[Mapping[str, str]] = None
