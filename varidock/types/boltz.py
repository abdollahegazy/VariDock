from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from varidock.types import (
    AF3InferenceOutput,
    Ligand,
    ProteinSequence
    )


@dataclass(frozen=False)
class MSAData:
    """
    Data for a single MSA, can store paired or unpaired or both.

    Attributes:
        paired (Optional[str]): The paired MSA data as a string, if available.
        unpaired (Optional[str]): The unpaired MSA data as a string, if available
        paired_path (Optional[Path]): Optional path to the paired MSA file.
        unpaired_path (Optional[Path]): Optional path to the unpaired MSA file.
    """
    paired: Optional[str] = None
    unpaired: Optional[str] = None
    paired_path : Optional[Path] = None
    unpaired_path : Optional[Path] = None

    def has_paired(self) -> bool:
        """
        Check if paired MSA data is available.
        """
        return self.paired is not None

    def has_unpaired(self) -> bool:
        """
        Check if unpaired MSA data is available.
        """
        return self.unpaired is not None

    def write_unpaired_a3m(self, path: Path) -> None:
        if self.unpaired is None:
            raise ValueError("No unpaired MSA data to write")
        Path(path).write_text(self.unpaired)
        self.unpaired_path = path



@dataclass
class BoltzInput:
    data_json_path: Path
    protein_chain_id: str
    ligand: Ligand
    output_dir: Path
    name: str

@dataclass
class BoltzOutput:
    output_dir: Path
    source_input: BoltzInput