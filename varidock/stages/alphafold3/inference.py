from dataclasses import replace

from varidock.execution.slurm import SlurmExecutor
from varidock.pipeline.stage import Stage
from varidock.runners.af3 import AF3Config, plan_af3
from varidock.execution import LocalExecutor
from varidock.types import AF3MergedInput, AF3InferenceOutput


class AF3Inference(Stage[AF3MergedInput, AF3InferenceOutput]):
    """Run AF3 inference for any W-mer complex with optional ligands. Requires pre-computed MSAs/templates from AF3MSA stage.

    Executes AF3 with the full pipeline to produce CIF output.

    Attributes:
        af3_config (AF3Config): Singularity/container configuration for AF3.
    """

    name = "af3_inference"
    input_type = AF3MergedInput
    output_type = AF3InferenceOutput

    def __init__(
        self,
        af3_config: AF3Config,
        jax_cache_dir: str,
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
                    "--norun_data_pipeline",
                    f"--jax_compilation_cache_dir={jax_cache_dir}",
                ),
            )
        self.af3_config = af3_config
        self.write_only = write_only
        self.overwrite_input = overwrite_input

    def run(self, input: AF3MergedInput) -> AF3InferenceOutput:
        """Run AF3 inference for a merged input.

        Args:
            input (AF3MergedInput): Prepared input with JSON path and output directory.

        Returns:
            AF3InferenceOutput: Output containing paths to CIF and data JSON.

        Raises:
            FileNotFoundError: If expected output CIF is not produced.

        """
        assert input.output_dir is not None, "AF3Inference requires an output directory in the input to run inference. For merging without inference, use AF3MSAMerger directly."
        
        input_json = input.json_path.resolve().read_text()

        plan = plan_af3(
            cfg=self.af3_config,
            name=input.name,
            input_json=input_json,
            output_dir=input.output_dir.resolve(),  # ensure absolute path
        )

        self.executor.execute(
            plan, write_only=self.write_only, overwrite_inputs=self.overwrite_input
        )

        data_json = (
            input.output_dir.resolve()
            / "af_output"
            / input.name
            / f"{input.name}_data.json"
        )

        cif = (
            input.output_dir.resolve()
            / "af_output"
            / input.name
            / f"{input.name}.cif"
        )

        if not self.write_only and not data_json.exists():
            raise FileNotFoundError(f"AF3 inference output not found: {data_json}")

        return AF3InferenceOutput(
            cif_path=cif,
            data_json_path=data_json,
            source_json_path=input.json_path,
        )   

