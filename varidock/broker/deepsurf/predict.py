#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 16:16:56 2020
@author: smylonas
"""

import os

from .network import Network
from .protein import Protein
from .bsite_extraction import Bsite_extractor


def predict(
    prot_file: str,
    model_path: str,
    output: str,
    model: str = "orig",
    f: int = 10,
    T: float = 0.9,
    batch: int = 32,
    voxel_size: float = 1.0,
    protonate: bool = False,
    expand: bool = False,
    discard_points: bool = False,
    seed: int | None = None,
):
    """Run DeepSurf pocket prediction."""
    if not os.path.exists(prot_file):
        raise IOError("%s does not exist." % prot_file)
    if not os.path.exists(model_path):
        raise IOError("%s does not exist." % model_path)
    if not os.path.exists(output):
        os.makedirs(output)

    prot = Protein(prot_file, protonate, expand, f, output, discard_points, seed)
    nn = Network(model_path, model, voxel_size)
    lig_scores = nn.get_lig_scores(prot, batch)
    extractor = Bsite_extractor(T)
    extractor.extract_bsites(prot, lig_scores)
