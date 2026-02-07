from __future__ import annotations

from dataclasses import dataclass

from varidock.plans import RunPlan
from varidock.execution.materialize import PlanMaterializer, DefaultMaterializer
from varidock.execution.run import CommandRunner, LocalCommandRunner, CompletedRun
from varidock.execution.validate import PlanValidator, ExpectedOutputsValidator

@dataclass
class LocalExecutor:
    materializer: PlanMaterializer = DefaultMaterializer()
    runner: CommandRunner = LocalCommandRunner(capture_output=False)
    validator: PlanValidator = ExpectedOutputsValidator()

    def execute(self, plan: RunPlan, write_only:bool = False, overwrite_inputs: bool = False) -> CompletedRun:
        self.materializer.materialize(plan, overwrite=overwrite_inputs)
        if write_only:
            return CompletedRun(returncode=0, argv=plan.argv, stdout="", stderr="")

        try:
            self.validator.validate(plan)
            # If we reach here, outputs already look good → skip execution
            return CompletedRun(
                returncode=0,
                argv=plan.argv,
                stdout="(skipped: outputs already valid)",
                stderr="",
            )
        except Exception:
            # Not valid yet → fall through and actually run
            pass
        
        result = self.runner.run(plan)
        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed (returncode={result.returncode}): {list(plan.argv)}\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}\n"
            )

        self.validator.validate(plan)
        return result
