# docking/structure/template.py
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass(frozen=True)
class TemplateData:
    templates: Optional[Any] = None  # AF3 JSON chunk
    materialized_dir: Optional[Path] = None
    template_ids: Optional[list[str]] = None  # extracted IDs
    alignment_path: Optional[Path] = None  # if you export later