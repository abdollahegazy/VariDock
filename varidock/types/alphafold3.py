from dataclasses import dataclass
from pathlib import Path

@dataclass
class AF3InferenceOutput:
    """Output from AF3 inference stage.

    Attributes:
        cif_path (Path): Path to the predicted structure CIF file.
        data_json_path (Path): Path to the AF3 output JSON containing MSA and template info.
        source_json_path (Path): Path to the input JSON used for this inference run.

    """

    cif_path: Path
    data_json_path: Path | None
    source_json_path: Path | None

@dataclass
class AF3MergedInput:
    """Assembled multimer input JSON ready for inference.

    Attributes:
        json_path (Path): Path to the merged AF3 input JSON.
        name (str): Job name for this complex.
        output_dir (Path | None): Root output directory for this AF3 run. Can be none when this is used to merge JSONs without running inference.
    """

    json_path: Path
    name: str
    output_dir: Path | None


@dataclass
class AF3MSAOutput:
    """Output from an AF3 MSA/data pipeline run.

    Attributes:
        data_json_path (Path): Path to the AF3 output JSON containing
            unpairedMsa, pairedMsa, and templates fields.
        protein_id (str): Identifier for the protein (e.g. 'AT3G62980').
        chain_id (str): Chain identifier used in the AF3 JSON.

    """

    data_json_path: Path
    protein_id: str
    chain_id: str


@dataclass
class AF3MSAInput:
    """Prepared input for a single-chain AF3 MSA run.

    Attributes:
        json_path (Path): Path to the AF3 input JSON file.
        output_dir (Path): Root directory for this protein's AF3 run
            (contains af_input/ and af_output/).
        chain_id (str): Chain identifier used in the AF3 JSON (e.g. 'A').
        protein_id (str): Identifier for the protein (e.g. 'AT3G62980').

    """

    json_path: Path
    output_dir: Path
    protein_id: str
    chain_id: str
