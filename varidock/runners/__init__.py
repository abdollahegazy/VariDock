"""Runners are responsible for executing the actual structure prediction code, such as AlphaFold. They take a configuration object and execute the prediction, returning the path to the predicted structure.

This module defines the base runner interface and specific implementations for different prediction tools. Each runner handles the details of preparing input files, invoking the prediction software (e.g., via Singularity), and managing outputs.
"""
from .base import StructurePredictionRunner
from .af3 import AF3Config

__all__ = [
    "StructurePredictionRunner",
    "AF3Config",
]