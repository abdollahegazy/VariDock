from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from varidock.plans import RunPlan


class PlanValidator(ABC):
    @abstractmethod
    def validate(self, plan: RunPlan) -> None:
        raise NotImplementedError


class ExpectedOutputsValidator(PlanValidator):
    def validate(self, plan: RunPlan) -> None:
        missing = [Path(p) for p in plan.expected_outputs if not Path(p).exists()]
        if missing:
            raise RuntimeError(f"Missing expected outputs: {missing}")
