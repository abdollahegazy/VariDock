"""The stage module defines the Stage protocol, which represents a single step in the structure prediction pipeline. Each stage has a name, input type, output type, and a run method that takes an input and produces an output. Stages can be composed together to form a complete pipeline for structure prediction.

A stage is a self-contained unit of work that transforms data from one form to another. For example, a stage might take a protein sequence as input and produce an AF3 input JSON as output. The Stage protocol allows us to define these transformations in a modular way, enabling flexible composition of different stages to create complex workflows.
"""
# varidock/pipeline/stage.py
from typing import Protocol, TypeVar

In = TypeVar("In")
Out = TypeVar("Out")


class Stage(Protocol[In, Out]):
    """Represents a single step in the structure prediction pipeline."""

    name: str
    input_type: type[In]
    output_type: type[Out]

    def run(self, input: In) -> Out: 
        """Execute the stage's transformation logic.

        :param input: The input data for the stage, which must be of the type specified by input_type.
        :return: The output data produced by the stage, which will be of the type specified by output_type.
        """
        ...