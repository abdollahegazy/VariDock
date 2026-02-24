"""Broker module for external tool integrations."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from varidock.broker.adfr import prepare_receptor
    from varidock.broker.deepsurf import predict
    from varidock.broker.meeko import meeko
    from varidock.broker.vina import vina

__all__ = [
    "prepare_receptor",
    "predict",
    "meeko",
    "vina",
]


def __getattr__(name):
    if name == "prepare_receptor":
        from varidock.broker.adfr import prepare_receptor

        return prepare_receptor
    elif name == "predict":
        from varidock.broker.deepsurf import predict

        return predict
    elif name == "meeko":
        from varidock.broker.meeko import meeko

        return meeko
    elif name == "vina":
        from varidock.broker.vina import vina

        return vina
    raise AttributeError(f"module 'varidock.broker' has no attribute {name}")
