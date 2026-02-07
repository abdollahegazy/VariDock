from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from docking.plans import RunPlan


class PlanMaterializer(ABC):
    @abstractmethod
    def materialize(self, plan: RunPlan, overwrite: bool = False) -> None:
        raise NotImplementedError


class DefaultMaterializer(PlanMaterializer):
    def materialize(self, plan: RunPlan, overwrite: bool = False) -> None:
        plan.work_dir.mkdir(parents=True, exist_ok=True)

        for path, text in plan.files_text.items():
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)

            if p.exists() and not overwrite:
                continue

            p.write_text(text)

