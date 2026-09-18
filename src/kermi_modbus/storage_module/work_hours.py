"""Betriebsstunden block (project plan §5.2, addresses 300-301).

Unlike the x-center's work-hours block (150-152), the Excel documents NO
scale factor here — raw hours, not tenths of an hour. See const.py.

The x-center's 0.1 factor (150-152) is now CONFIRMED against real hardware
(project plan §9, 2026-09-11) — it was previously flagged here as the
"suspect" one, but that concern didn't hold up (see const.py / xcenter/
work_hours.py for the measured values). These two storage-module registers
(300-301) have NOT themselves been read from real hardware yet — they
remain as documented (no scale) until they get the same treatment.
"""

from __future__ import annotations

from modbus_connection.model import Component, integer

from .. import const


class WorkHours(Component):
    """Runtime counters. Call ``async_update()`` to refresh."""

    heating_circuit_pump = integer(const.STORAGE_HEATING_CIRCUIT_PUMP_WORKHOURS.address, signed=False, unit="h")
    heating_rod = integer(const.STORAGE_HEATING_ROD_WORKHOURS.address, signed=False, unit="h")
