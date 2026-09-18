"""Energiequelle block (project plan §5.1, x-center addresses 1-3)."""

from __future__ import annotations

from modbus_connection.model import Component, gauge

from .. import const


class EnergySource(Component):
    """Heat-source air temperatures. Call ``async_update()`` to refresh."""

    exit_temperature = gauge(const.XCENTER_EXIT_TEMPERATURE.address, const.XCENTER_EXIT_TEMPERATURE.scale, signed=True, unit="°C")
    incoming_temperature = gauge(const.XCENTER_INCOMING_TEMPERATURE.address, const.XCENTER_INCOMING_TEMPERATURE.scale, signed=True, unit="°C")
    outside_temperature = gauge(const.XCENTER_OUTSIDE_TEMPERATURE.address, const.XCENTER_OUTSIDE_TEMPERATURE.scale, signed=True, unit="°C")
