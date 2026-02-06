# docking/api.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Sequence

from docking.jobs import PredictionJob
from docking.plans import RunPlan
from docking.execution import LocalExecutor
from docking.runners.af3 import AF3Runner, AF3Config
from docking.runners.boltz import BoltzRunner, BoltzConfig


def _get_env(name: str) -> str:
    val = os.environ.get(name)
    if val is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return val


def _load_af3_config() -> AF3Config:
    return AF3Config(
        sif_path=Path(_get_env("AF3_SIF_PATH")),
        model_dir=Path(_get_env("AF3_MODEL_DIR")),
        db_dir=Path(_get_env("AF3_DB_DIR")),
        runner_script=Path(_get_env("AF3_RUNNER_SCRIPT")),
    )


def _load_boltz_config() -> BoltzConfig:
    return BoltzConfig(
        accelerator=os.environ.get("BOLTZ_ACCELERATOR", "gpu"),
    )


RUNNERS = {
    "af3": (AF3Runner, _load_af3_config),
    "boltz": (BoltzRunner, _load_boltz_config),
}


def dock(
    *,
    name: str,
    protein_sequences: Sequence[str],
    protein_chain_ids: Sequence[str],
    output_dir: Path | str,
    method: str = "af3",
    ligand_smiles: Optional[str] = None,
    ligand_id: Optional[str] = None,
    msa_paths: Optional[Sequence[Path | str]] = None,
    af3_output_dir: Optional[Path | str] = None,
    seed: int = 42,
    dry_run: bool = False,
) -> RunPlan:
    """
    Run docking with the specified method.

    Methods:
        "af3"   - AlphaFold3
        "boltz" - Boltz (requires msa_paths or af3_output_dir)
    """
    if method not in RUNNERS:
        raise ValueError(
            f"Unknown method: {method}. Expected one of: {list(RUNNERS.keys())}"
        )

    output_dir = Path(output_dir)
    if msa_paths is not None:
        msa_paths = [Path(p) for p in msa_paths]
    if af3_output_dir is not None:
        af3_output_dir = Path(af3_output_dir)

    job = PredictionJob(
        name=name,
        protein_sequences=list(protein_sequences),
        protein_chain_ids=list(protein_chain_ids),
        output_dir=output_dir,
        ligand_smiles=ligand_smiles,
        ligand_id=ligand_id,
        msa_paths=msa_paths,
        af3_output_dir=af3_output_dir,
        seed=seed,
    )

    runner_cls, config_loader = RUNNERS[method]
    cfg = config_loader()
    runner = runner_cls(cfg)
    plan = runner.plan(job)

    if not dry_run:
        executor = LocalExecutor()
        executor.execute(plan)

    return plan
