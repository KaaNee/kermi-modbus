"""Base class for Kermi model profiles.

Unlike E3DC (see e3dc-modbus), Kermi's register list documents no
manufacturer/model/serial-number identification registers anywhere for the
x-center or the storage module — there is currently no known register to
read during setup that would tell two Kermi models apart. So, unlike
``E3DCDevice.async_probe()``, ``KermiDevice`` cannot detect which model is
connected by reading the device; the caller must say which profile to use
(``KermiDevice(..., profile=...)``, default: the one verified profile).

If a real identification register is found later (e.g. from a firmware
update, a newer Kermi doc revision, or a support request to Kermi), a
``matches()``-based probe like E3DC's can be added here without touching the
subsystem classes — this is why the profile stays a separate object instead
of being folded into ``KermiDevice`` directly.
"""

from __future__ import annotations

from abc import ABC
from typing import ClassVar


class KermiModelProfile(ABC):
    """Common interface every Kermi model profile must implement."""

    #: Human-readable model name, e.g. "x-change dynamic pro".
    name: ClassVar[str]

    #: Whether this model's x-center exposes the PV-modulation block
    #: (addresses 300-303). Documented for the x-change dynamic pro; not
    #: confirmed for any other Kermi/Bösch model.
    has_pv_modulation: ClassVar[bool] = True
