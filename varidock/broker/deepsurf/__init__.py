"""DeepSurf binding site prediction module.

This module provides functionality for predicting protein binding sites
using the DeepSurf deep learning approach based on 3D convolutional
neural networks.
"""

from .predict import predict

__all__ = ["predict"]