"""The jobs module defines the core data structures for representing structure prediction jobs. This includes the PredictionJob class, which encapsulates all the necessary information about a prediction task, such as the input sequences, configuration parameters, and metadata. This module serves as the foundation for defining what a structure prediction job looks like and how it should be executed by the runners."""
# varidock/jobs/__init__.py
from .jobs import PredictionJob

__all__ = ["PredictionJob"]