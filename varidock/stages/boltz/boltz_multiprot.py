from dataclasses import dataclass
import os
from typing import Dict,Tuple
from varidock.pipeline.stage import Stage
from varidock.io.af3_load import extract_msas_from_af3_output
from varidock.io.boltz_yaml import _build_boltz_yaml_multi_prot
from varidock.types import BoltzInputMulti, BoltzOutput, MSAData
from varidock.utils import run_with_interrupt


@dataclass
class BoltzConfig:
    accelerator: str = "gpu"
    pytorch_cuda_alloc_conf: str = "max_split_size_mb:64"
    extra_args: tuple[str, ...] = (
        "--override",
        "--output_format",
        "pdb",
    )


class BoltzPredict(Stage[BoltzInputMulti, BoltzOutput]):
    name = "boltz_predict"
    input_type = BoltzInputMulti
    output_type = BoltzOutput

    def __init__(self, config: BoltzConfig):
        self.config = config

    def run(self, input: BoltzInputMulti, write_only: bool = False) -> BoltzOutput:
        input_dir = input.output_dir / "boltz_input"
        output_dir = input.output_dir / "boltz_output"
        input_dir.mkdir(parents=True, exist_ok=True)
    
        assert input.ligand.smiles is not None or input.ligand.ccd is not None, (
            "Ligand information is missing. Must provide either SMILES or CCD data."
        )

        chain_ids = list(input.data_json_paths.keys())
        # chain id -> (MSAData, sequence)
        unpaired_msas: Dict[str, Tuple[MSAData,str]] = {}
        for  chain_id, data_json_path in input.data_json_paths.items():
            result = extract_msas_from_af3_output(data_json_path)
            if result is None:
                raise RuntimeError(f"No protein found in {data_json_path}")
            msa, sequence = result
            if not msa.has_unpaired():
                raise RuntimeError(f"No unpaired MSA found in {data_json_path}")
            unpaired_msas[chain_id] = (msa, sequence)
            
        if len(unpaired_msas) != len(chain_ids):
            raise RuntimeError(f"Found unpaired MSAs for {len(unpaired_msas)} chains but expected {len(chain_ids)} based on input chain IDs")

        for chain_id in chain_ids:
            msa, sequence = unpaired_msas[chain_id]
            msa_path = input_dir / f"{chain_id}_unpaired.a3m"
            msa.write_unpaired_a3m(msa_path)
        ccd = True if input.ligand.ccd is not None and input.ligand.smiles is None else False
        
        if ccd and input.ligand.smiles:
            print("[WARNING]: Both CCD and SMILES provided for ligand, defaulting to CCD")

        ligand = input.ligand.ccd if ccd else input.ligand.smiles
        if ligand is None:
            raise ValueError("Ligand information is missing. Must provide either SMILES or CCD data.")
        
        yaml_str = _build_boltz_yaml_multi_prot(
            protein_sequences=[unpaired_msas[chain_id][1] for chain_id in chain_ids],
            protein_chain_ids=chain_ids,
            msa_path_map={chain_id: input_dir / f"{chain_id}_unpaired.a3m" for chain_id in chain_ids},
            ligand_chain_id=input.ligand.af3_sequence_id or "B",
            ligand=ligand,
            ccd=ccd
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

        if write_only:
            return BoltzOutput(
                output_dir=output_dir,
                source_input=input,
            )
        
        run_with_interrupt(cmd, env=env)

        return BoltzOutput(
            output_dir=output_dir,
            source_input=input,
        )

from varidock.types import Ligand
from pathlib import Path

test = BoltzInputMulti(
    data_json_paths={
        "C": Path("/serviceberry/tank/abdolla/PRIME/data/MSAs/cor/AT1G72450/af_output/AT1G72450/AT1G72450_data.json"),
        "F": Path("/serviceberry/tank/abdolla/PRIME/data/MSAs/fbox/AT2G39940/af_output/AT2G39940/AT2G39940_data.json"),
    },
    ligand=Ligand(
        name='ligand',
        ccd="JAA"
    ),
    output_dir=Path("./"),
    name="test_prediction",
)

pred = BoltzPredict(BoltzConfig()).run(test, write_only=False)