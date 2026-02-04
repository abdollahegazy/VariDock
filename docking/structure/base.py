# docking/structure/base.py
from dataclasses import dataclass,field
from pathlib import Path
from typing import Optional

from .msa import MSAData
from .template import TemplateData


@dataclass(frozen=True)
class BaseStructure:
    root: Path
    backend: str

    data_json: Optional[Path] = None  # e.g. jobname_data.json
    sequence_id: Optional[str] = None  # or index; runner decides

    model_cif: Optional[Path] = None
    confidences_json: Optional[Path] = None
    summary_confidences_json: Optional[Path] = None
    ranking_csv: Optional[Path] = None

    msa: Optional[MSAData] = None
    templates: Optional[TemplateData] = None

    artifacts: dict[str, Path] = field(default_factory=dict)

    def has_msa(self) -> bool:
        return self.msa is not None
    def has_templates(self) -> bool:
        return self.templates is not None