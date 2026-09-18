"""Kermi model profiles. See _base.py for why there is no ``async_probe``."""

from __future__ import annotations

from ._base import KermiModelProfile
from .x_change_dynamic_pro import XChangeDynamicProProfile

__all__ = [
    "KermiModelProfile",
    "XChangeDynamicProProfile",
]
