# docking/structure/msa.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class MSAData:
    paired: Optional[str] = None
    unpaired: Optional[str] = None

    def has_paired(self) -> bool:
        return self.paired is not None

    def has_unpaired(self) -> bool:
        return self.unpaired is not None        


    def write_unpaired_a3m(self, path: Path) -> None:
        if self.unpaired is None:
            raise ValueError("No unpaired MSA data to write")
        Path(path).write_text(self.unpaired)