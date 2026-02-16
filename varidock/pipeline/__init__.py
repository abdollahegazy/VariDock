"""The pipeline module defines the core Pipeline class, which orchestrates the entire structure prediction process. It manages the sequence of stages, handles data flow between stages, and provides a high-level interface for running predictions."""
# varidock/pipeline/__init__.py
from varidock.pipeline.pipeline import Pipeline
from varidock.pipeline.stage import Stage


__all__ = [
    "Pipeline",
    "Stage",
]
