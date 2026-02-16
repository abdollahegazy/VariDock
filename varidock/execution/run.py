from __future__ import annotations

import os
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Sequence

from varidock.plans import RunPlan

@dataclass(frozen=True)
class CompletedRun:
    returncode: int
    argv: Sequence[str]
    stdout: Optional[str] = None
    stderr: Optional[str] = None


class CommandRunner(ABC):
    @abstractmethod
    def run(self, plan: RunPlan) -> CompletedRun:
        raise NotImplementedError


class LocalCommandRunner(CommandRunner):
    def __init__(self, capture_output: bool = False):
        self.capture_output = capture_output

    def run(self, plan: RunPlan) -> CompletedRun:
        env = os.environ.copy()
        if plan.env:
            env.update({k: str(v) for k, v in plan.env.items()})
    
        proc = subprocess.run(
            list(plan.argv),
            cwd=str(plan.work_dir),
            env=env,
            check=False,
            text=True,
            capture_output=self.capture_output,
        )

        return CompletedRun(
            returncode=proc.returncode,
            argv=plan.argv,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
