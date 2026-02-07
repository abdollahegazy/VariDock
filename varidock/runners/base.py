# docking/runners/base.py
from abc import ABC, abstractmethod
from varidock.jobs import PredictionJob
from varidock.plans import RunPlan


class StructurePredictionRunner(ABC):
    """
    Backend-specific logic that converts a PredictionJob
    into a concrete RunPlan.
    """

    @abstractmethod
    def plan(self, job: PredictionJob) -> RunPlan:
        """
        Produce a fully specified execution plan:
        - what files to write
        - what command to run
        - what outputs to expect
        """
        raise NotImplementedError