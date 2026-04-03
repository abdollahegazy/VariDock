from dataclasses import dataclass
import os
# from pathlib import Path

from varidock.pipeline.stage import Stage
from varidock.io.af3_load import extract_msas_from_af3_output
from varidock.io.boltz_yaml import build_boltz_yaml
from varidock.types import BoltzInput, BoltzOutput
# from varidock.types.shared import Ligand
from varidock.utils import run_with_interrupt


@dataclass
class BoltzConfig:
    accelerator: str = "gpu"
    pytorch_cuda_alloc_conf: str = "max_split_size_mb:64"
    extra_args: tuple[str, ...] = ("--override","--output_format","pdb",)


class BoltzPredict(Stage[BoltzInput, BoltzOutput]):
    name = "boltz_predict"
    input_type = BoltzInput
    output_type = BoltzOutput

    def __init__(self, config: BoltzConfig):
        self.config = config

    def run(self, input: BoltzInput, write_only: bool = False) -> BoltzOutput:
        input_dir = input.output_dir / "boltz_input"
        output_dir = input.output_dir / "boltz_output"
        input_dir.mkdir(parents=True, exist_ok=True)

        assert input.data_json_path is not None, (
            "BoltzInput must have a data_json_path to extract MSAs"
        )
        assert input.ligand.smiles is not None, (
            "BoltzPredict currently requires ligand SMILES"
        )

        result = extract_msas_from_af3_output(input.data_json_path)
        if result is None:
            raise RuntimeError(f"No protein found in {input.data_json_path}")

        msa, sequence = result
        if not msa.has_unpaired():
            raise RuntimeError(f"No unpaired MSA found in {input.data_json_path}")

        msa_path = input_dir / f"{input.protein_chain_id}_unpaired.a3m"
        msa.write_unpaired_a3m(msa_path)

        yaml_str = build_boltz_yaml(
            protein_sequence=sequence,
            protein_chain_id=input.protein_chain_id,
            msa_path=msa_path,
            ligand_smiles=input.ligand.smiles,
            ligand_chain_id=input.ligand.af3_sequence_id or "B",
        )
        yaml_path = input_dir / f"{input.name}.yaml"
        yaml_path.write_text(yaml_str)

        cmd = [
            "boltz",
            "predict",
            str(yaml_path),
            "--accelerator",
            self.config.accelerator,
            "--out_dir",
            str(output_dir),
            *self.config.extra_args,
        ]

        env = {
            **os.environ,
            "PYTORCH_CUDA_ALLOC_CONF": self.config.pytorch_cuda_alloc_conf,
        }

        if not write_only:
            run_with_interrupt(cmd, env=env)

        return BoltzOutput(
            output_dir=output_dir,
            source_input=input,
        )

# boltz_input = BoltzInput(
#     data_json_path=Path(
#         "/serviceberry/tank/abdolla/SMBA/expiremental_affinities/data/MSA/P04757/af_output/P04757/P04757_data.json"
#     ),
#     protein_chain_id="P",
#     ligand=Ligand(
#         name="TestLigand",
#         smiles="CCO",
#         af3_sequence_id="L",
#     ),
#     output_dir=Path("./"),
#     name="test_case",
# )
# cfg = BoltzConfig()
# boltz_predict_stage = BoltzPredict(config=cfg)

# boltz_predict_stage.run(boltz_input)