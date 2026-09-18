"""Ladekreis block (project plan §5.1, x-center addresses 50-52)."""

from __future__ import annotations

from modbus_connection.model import Component, gauge

from .. import const


class ChargingCircuit(Component):
    """Heat pump flow/return water. Call ``async_update()`` to refresh."""

    flow_temperature = gauge(const.XCENTER_FLOW_TEMPERATURE.address, const.XCENTER_FLOW_TEMPERATURE.scale, signed=True, unit="°C")
    return_temperature = gauge(const.XCENTER_RETURN_TEMPERATURE.address, const.XCENTER_RETURN_TEMPERATURE.scale, signed=True, unit="°C")
    flow_speed = gauge(const.XCENTER_FLOW_SPEED.address, const.XCENTER_FLOW_SPEED.scale, signed=False, unit="l/min")
