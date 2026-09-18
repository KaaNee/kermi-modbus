"""Betriebsstunden block (project plan §5.1, x-center addresses 150-152).

The 0.1 h scale factor here is CONFIRMED against real hardware (2026-09-11,
via script/query.py): register 152 raw = 59232 -> 5923.2 h, and register 150
(fan) independently decodes to 5892.9 h — the near-identical values for fan
and compressor are exactly what's physically expected (a heat pump's fan
runs whenever the compressor does), which is strong corroborating evidence
that 0.1 is correct, not an off-by-one on the scale.

The earlier "~9 months implausible" concern (still in git history) conflated
CALENDAR time since installation with cumulative COMPRESSOR RUNTIME — a
compressor cycles on/off with demand, so ~5900 h of runtime over ~3 calendar
years is entirely ordinary. The uint16-at-0.1-scale ceiling (6553.5 h) is a
genuine long-term register-design limitation (it will eventually wrap on a
long-lived, heavily-used unit) — worth knowing, but it was never evidence
against the *current* factor, which is now measured, not guessed.
"""

from __future__ import annotations

from modbus_connection.model import Component, gauge

from .. import const


class WorkHours(Component):
    """Runtime counters. Call ``async_update()`` to refresh."""

    fan = gauge(const.XCENTER_WORKHOURS_FAN.address, const.XCENTER_WORKHOURS_FAN.scale, signed=False, unit="h")
    storage_loading_pump = gauge(const.XCENTER_WORKHOURS_STORAGE_LOADING_PUMP.address, const.XCENTER_WORKHOURS_STORAGE_LOADING_PUMP.scale, signed=False, unit="h")
    compressor = gauge(const.XCENTER_WORKHOURS_COMPRESSOR.address, const.XCENTER_WORKHOURS_COMPRESSOR.scale, signed=False, unit="h")
