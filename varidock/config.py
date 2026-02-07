from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import os
import tomllib


VARIDOCK_CONFIG_DIR = Path.home() / ".varidock"
VARIDOCK_CONFIG_FILE = VARIDOCK_CONFIG_DIR / "config.toml"


@dataclass
class AF3Settings:
    sif_path: Path | None = None
    model_dir: Path | None = None
    db_dir: Path | None = None
    runner_script: Path | None = None


@dataclass
class DeepSurfSettings:
    model_dir: Path | None = None


@dataclass
class VaridockConfig:
    af3: AF3Settings = field(default_factory=AF3Settings)
    deepsurf: DeepSurfSettings = field(default_factory=DeepSurfSettings)

    @classmethod
    def load(cls) -> "VaridockConfig":
        """Load config from file, with env var overrides."""
        config = cls()

        # 1. Load from config file
        if VARIDOCK_CONFIG_FILE.exists():
            with open(VARIDOCK_CONFIG_FILE, "rb") as f:
                raw = tomllib.load(f)
            config = _apply_toml(config, raw)

        # 2. Env vars override
        config = _apply_env(config)

        return config


def _apply_toml(config: VaridockConfig, raw: dict[str, Any]) -> VaridockConfig:
    if "af3" in raw:
        af3 = raw["af3"]
        config.af3 = AF3Settings(
            sif_path=Path(af3["sif_path"]) if "sif_path" in af3 else None,
            model_dir=Path(af3["model_dir"]) if "model_dir" in af3 else None,
            db_dir=Path(af3["db_dir"]) if "db_dir" in af3 else None,
            runner_script=Path(af3["runner_script"])
            if "runner_script" in af3
            else None,
        )
    if "deepsurf" in raw:
        ds = raw["deepsurf"]
        config.deepsurf = DeepSurfSettings(
            model_dir=Path(ds["model_dir"]) if "model_dir" in ds else None,
        )
    return config


def _apply_env(config: VaridockConfig) -> VaridockConfig:
    if v := os.environ.get("AF3_SIF_PATH"):
        config.af3.sif_path = Path(v)
    if v := os.environ.get("AF3_MODEL_DIR"):
        config.af3.model_dir = Path(v)
    if v := os.environ.get("AF3_DB_DIR"):
        config.af3.db_dir = Path(v)
    if v := os.environ.get("AF3_RUNNER_SCRIPT"):
        config.af3.runner_script = Path(v)
    if v := os.environ.get("DEEPSURF_MODEL_DIR"):
        config.deepsurf.model_dir = Path(v)
    return config
