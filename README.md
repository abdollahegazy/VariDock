# VariDock

[![PyPI version](https://img.shields.io/pypi/v/varidock.svg)](https://pypi.python.org/pypi/varidock/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/varidock.svg)](https://pypi.python.org/pypi/varidock/)
[![Docs](https://img.shields.io/badge/docs-gh--pages-brightgreen?logo=github)](https://lonelyneutrin0.github.io/varidock/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A modular pipeline for cross-species protein–ligand virtual screening, combining structure prediction, molecular dynamics, pocket detection, and ensemble docking into a reproducible, HPC-ready workflow.

## Overview

VariDock automates the full path from protein sequence to docked binding poses:

1. **Structure prediction** — AlphaFold 3 co-folding with pre-computed MSA reuse across combinatorial protein–ligand screens
2. **Molecular dynamics** — NAMD-based simulations to generate conformational ensembles and validate predicted complexes
3. **Pocket detection** — DeepSurf-based identification of binding sites on MD-sampled frames
4. **Virtual screening** — AutoDock Vina ensemble docking across multiple receptor conformations

Each step is a composable *stage* with typed inputs and outputs, making it straightforward to swap tools, extend to new species, or run partial workflows.

## Installation

```bash
pip install varidock
```

For development:

```bash
git clone https://github.com/lonelyneutrin0/varidock.git
cd varidock
pip install -e ".[dev]"
```

## Quick Start

```python
from pathlib import Path
from varidock.stages import AF3InputBuilder, AF3MSAStage, AF3MSAMerger, AF3MSAMergerConfig
from varidock.runners.af3 import AF3Config
from varidock.types import ProteinSequence, Ligand

# 1. Build monomer input JSONs
builder = AF3InputBuilder(output_dir=Path("data/msa/fbox"), chain_id="F")
msa_input = builder.run(ProteinSequence(name="AT3G62980", sequence="MKVLF..."))

# 2. Run MSA (requires AF3 Singularity image + databases)
af3_cfg = AF3Config.from_config(script_args=("--norun_inference",))
msa_output = AF3MSAStage(af3_cfg).run(msa_input)

# 3. Merge monomer MSAs into a dimer + ligand input
merger = AF3MSAMerger(AF3MSAMergerConfig(output_dir=Path("data/complexes/IAC")))
merged = merger.run(
    msa_outputs=[fbox_msa, cor_msa],
    ligands=[Ligand(name="auxin", ccd="IAC", af3_sequence_id="L")],
)
```

## Pipeline Architecture

VariDock uses a stage-based architecture where each processing step is an independent, typed unit:

```
ProteinSequence
      │
      ▼
┌─────────────────┐
│ AF3InputBuilder  │  Build AF3 input JSON (per monomer)
└────────┬────────┘
         ▼
┌─────────────────┐
│  AF3MSAStage     │  Run MSA/template search (CPU, --norun_inference)
└────────┬────────┘
         ▼
┌─────────────────┐
│  AF3MSAMerger    │  Combine monomer MSAs + ligand into multimer JSON
└────────┬────────┘
         ▼
┌─────────────────┐
│ AF3InferenceStage│  Run structure prediction (GPU, --norun_data_pipeline)
└────────┬────────┘
         ▼
        CIF
         │
         ▼
┌─────────────────┐
│   CIFToPDB       │  Convert to PDB format
└────────┬────────┘
         ▼
┌─────────────────┐
│   MD Simulation   │  NAMD molecular dynamics
└────────┬────────┘
         ▼
┌─────────────────┐
│  Pocket Detection │  DeepSurf binding site identification
└────────┬────────┘
         ▼
┌─────────────────┐
│  Ensemble Docking │  AutoDock Vina across conformations
└─────────────────┘
```

Stages communicate through typed dataclasses, and execution is decoupled via executors (`LocalExecutor`, `SlurmExecutor`) so the same pipeline runs on a laptop or an HPC cluster.

## HPC / SLURM Support

VariDock is designed for large-scale screens on HPC clusters. The MSA stage supports sharded genetic databases for parallel search across many cores:

```python
from varidock.runners.af3 import AF3Config, sharded_script_args

af3_cfg = AF3Config.from_config(script_args=(
    "--norun_inference",
    *sharded_script_args(jackhmmer_n_cpu=2, jackhmmer_max_shards=16),
))
```

## Configuration

VariDock reads from a `varidock.toml` config file for paths to external tools:

```toml
[af3]
sif_path = "/path/to/alphafold3.sif"
model_dir = "/path/to/models"
db_dir = "/path/to/databases"
runner_script = "/path/to/run_alphafold.py"
```

Load with:

```python
af3_cfg = AF3Config.from_config()
```

## Requirements

- Python ≥ 3.10
- AlphaFold 3 (Singularity image + model parameters + genetic databases)
- NAMD (for MD simulations)
- AutoDock Vina + Meeko (for docking)
- Open Babel (for format conversions)

## License

VariDock is available under the MIT License. See [LICENSE](LICENSE) for details.

## Citation

If you use VariDock in your research, please cite:

```
@software{varidock,
  title={VariDock: Cross-species protein-ligand virtual screening pipeline},
  url={https://github.com/lonelyneutrin0/varidock},
}
```