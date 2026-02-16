"""The pipeline module defines the core Pipeline class, which orchestrates the entire structure prediction process. It manages the sequence of stages, handles data flow between stages, and provides a high-level interface for running predictions."""
# varidock/pipeline/pipeline.py 
from varidock.pipeline.stage import Stage


class Pipeline:
    """Orchestrates a sequence of stages to run a complete structure prediction workflow.

    The Pipeline class manages a list of stages, ensuring that the output type of each stage matches the input type of the next stage. It provides an add() method to append stages to the pipeline, and a run() method to execute the stages in sequence, passing the output of one stage as the input to the next.
    """

    def __init__(self, *stages: Stage):
        """Initialize the pipeline with an optional sequence of stages. It validates that the stages are compatible in terms of input and output types.
        
        :param self:  The instance of the Pipeline being created.
        :param stages: A variable number of Stage instances to initialize the pipeline with. Each stage must have compatible input and output types with the adjacent stages.
        :type stages: Stage
        """
        self.stages: list[Stage] = []
        for stage in stages:
            self.add(stage)

    def add(self, stage: Stage) -> "Pipeline":
        """Add a stage to the pipeline, ensuring type compatibility with the previous stage.
        
        :param self: The instance of the Pipeline to which the stage is being added.
        :param stage:  The Stage instance to add to the pipeline. The input type of this stage must match the output type of the last stage in the pipeline (if any).
        :type stage: Stage
        :return: The Pipeline instance itself, allowing for method chaining.
        :rtype: Pipeline
        """
        if self.stages:
            prev_output = self.stages[-1].output_type
            curr_input = stage.input_type
            if prev_output != curr_input:
                raise TypeError(
                    f"Stage '{stage.name}' expects {curr_input.__name__}, "
                    f"but previous stage outputs {prev_output.__name__}"
                )
        self.stages.append(stage)
        return self

    def run(self, input):
        """Execute the pipeline by running each stage in sequence, passing the output of one stage as the input to the next.
        
        :param self: The instance of the Pipeline being executed.
        :param input: The initial input to the pipeline, which must be compatible with the input type of the first stage.
        :return: The final output after processing through all stages of the pipeline.
        """
        result = input
        for stage in self.stages:
            result = stage.run(result)
        return result