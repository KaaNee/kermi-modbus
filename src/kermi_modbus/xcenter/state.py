"""Status + Statusmeldungen blocks (project plan §5.1, x-center addresses 200/250).

Both registers are plain uint16 values, not bit-packed — see const.py's
comment on XCENTER_GLOBAL_STATE (openHAB's ``StateDTO`` misreads this
register with ``extractBit()``, a bug in that binding, not a device
property). No ``nan`` sentinel is configured — "0" (Standby / no alarm) is a
valid, common state.
"""

from __future__ import annotations

from modbus_connection.model import Component, enum, integer

from .. import const
from ..enums import GlobalState


class State(Component):
    """Global operating state. Call ``async_update()`` to refresh."""

    global_state = enum(const.XCENTER_GLOBAL_STATE.address, GlobalState, signed=False)


class Alarm(Component):
    """Global alarm flag. Call ``async_update()`` to refresh.

    Plain 0/1 register, kept as ``int`` rather than a dedicated enum type —
    a single boolean flag isn't worth a shared enums.py type.
    """

    active = integer(const.XCENTER_ALARM_ACTIVE.address, signed=False)
