"""Serves as the initialization module for the `varidock.io` package, which provides input/output functionalities for the Varidock project. This module imports and exposes key functions from submodules such as `af3_json` and `fasta`, allowing users to easily access these functionalities when they import the `varidock.io` package. The `__all__` variable is defined to specify the public API of this package, ensuring that only the intended functions are accessible when using wildcard imports."""
# varidock/io/__init__.py
from .af3_json import build_af3_input_json
from .fasta import _read_single_fasta
__all__ = ["build_af3_input_json", "_read_single_fasta"]