# ./varidock/stages/AF3Input.py
from pathlib import Path

from varidock.pipeline.stage import Stage
from varidock.types import AF3MSAInput, ProteinSequence
from varidock.io.af3_json import build_af3_input_json

class AF3InputBuilder(Stage[ProteinSequence, AF3MSAInput]):
    """Build an AF3 input JSON for a single monomer chain.

    Used to prepare inputs for the MSA/data pipeline stage (--norun_inference).
    Protein gets its own subdirectory under output_dir.

    Attributes:
        output_dir (Path): Parent directory where per-protein subdirectories are created.
        chain_id (str): Chain identifier used in the AF3 JSON (default 'A').

    """

    name = "af3_input_builder"
    input_type = ProteinSequence
    output_type = AF3MSAInput


    def __init__(self, output_dir: Path, chain_id: str = "A"):
        self.output_dir = output_dir
        self.chain_id = chain_id

    def run(self, input: ProteinSequence) -> AF3MSAInput:
        """Generate the AF3 input JSON and write it to disk.

        Args:
            input (ProteinSequence): Protein with name and sequence to build the JSON for.

        Returns:
            AF3MSAInput: Prepared input pointing to the written JSON and output directory.

        """
        job_dir = self.output_dir / input.name
        json_path = job_dir / "af_input" / f"{input.name}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)

        json_text = build_af3_input_json(
            name=input.name,
            sequences=[input.sequence],
            chain_ids=[self.chain_id],
        )

        json_path.write_text(json_text)

        return AF3MSAInput(
            json_path=json_path,
            output_dir=job_dir,
            protein_id=input.name,
            chain_id=self.chain_id,
        )
