from varidock.pipeline.stage import Stage


class Pipeline:
    def __init__(self, *stages: Stage):
        self.stages: list[Stage] = []
        for stage in stages:
            self.add(stage)

    def add(self, stage: Stage) -> "Pipeline":
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
        result = input
        for stage in self.stages:
            result = stage.run(result)
        return result