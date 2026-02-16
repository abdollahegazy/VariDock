from dataclasses import replace

from varidock.execution.slurm import SlurmExecutor
from varidock.pipeline.stage import Stage
from varidock.runners.af3 import AF3Config, plan_af3
from varidock.execution import LocalExecutor
from varidock.types import AF3MSAInput, AF3MSAOutput


class AF3MSA(Stage[AF3MSAInput, AF3MSAOutput]):
    """Run AF3 data pipeline (MSA + template search) for a single monomer.

    Executes AF3 with --norun_inference to produce a JSON augmented with
    pre-computed MSAs and templates, without running model inference.

    Attributes:
        af3_config (AF3Config): Singularity/container configuration for AF3.
        write_only (bool): If True, write files but don't execute (dry run).

    """

    name = "af3_msa"
    input_type = AF3MSAInput
    output_type = AF3MSAOutput

    def __init__(
        self,
        af3_config: AF3Config,
        executor: LocalExecutor | SlurmExecutor | None = None,
        write_only: bool = True,
        overwrite_input: bool = False,
    ):
        self.executor = executor or LocalExecutor()
        
        if "--norun_inference" not in af3_config.script_args:
            af3_config = replace(
                af3_config,
                script_args=(
                    *af3_config.script_args,
                    "--norun_inference",
                ),
            )
        self.af3_config = af3_config
        self.write_only = write_only
        self.overwrite_input = overwrite_input

    def run(self, input: AF3MSAInput) -> AF3MSAOutput:
        """Run AF3 MSA/data pipeline for a single protein.

        Args:
            input (AF3MSAInput): Prepared input with JSON path and output directory.

        Returns:
            AF3MSAOutput: Path to the output data JSON containing MSA results.

        Raises:
            FileNotFoundError: If expected output JSON is not produced.

        """
        input_json = input.json_path.read_text()

        plan = plan_af3(
            cfg=self.af3_config,
            name=input.protein_id,
            input_json=input_json,
            output_dir=input.output_dir,
        )

        self.executor.execute(plan, write_only=self.write_only,overwrite_inputs=self.overwrite_input)

        data_json = (
            input.output_dir
            / "af_output"
            / input.protein_id.lower()
            / f"{input.protein_id.lower()}_data.json"
        )

        if not self.write_only and not data_json.exists():
            raise FileNotFoundError(f"AF3 MSA output not found: {data_json}")

        return AF3MSAOutput(
            data_json_path=data_json,
            protein_id=input.protein_id,
            chain_id=input.chain_id,
        )
