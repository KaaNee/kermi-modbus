"""Freie Fühler + Außentemperatur block (project plan §5.2, addresses 250-255)."""

from __future__ import annotations

from modbus_connection.model import Component, gauge

from .. import const


class Sensors(Component):
    """Four general-purpose probes + outside temperature.

    Call ``async_update()`` to refresh.
    """

    probe_1 = gauge(const.STORAGE_SENSOR_1.address, const.STORAGE_SENSOR_1.scale, signed=True, unit="°C")
    probe_2 = gauge(const.STORAGE_SENSOR_2.address, const.STORAGE_SENSOR_2.scale, signed=True, unit="°C")
    probe_3 = gauge(const.STORAGE_SENSOR_3.address, const.STORAGE_SENSOR_3.scale, signed=True, unit="°C")
    probe_4 = gauge(const.STORAGE_SENSOR_4.address, const.STORAGE_SENSOR_4.scale, signed=True, unit="°C")
    outside_temperature = gauge(const.STORAGE_OUTSIDE_TEMPERATURE.address, const.STORAGE_OUTSIDE_TEMPERATURE.scale, signed=True, unit="°C")
    outside_temperature_averaged = gauge(const.STORAGE_OUTSIDE_TEMPERATURE_AVERAGED.address, const.STORAGE_OUTSIDE_TEMPERATURE_AVERAGED.scale, signed=True, unit="°C")
