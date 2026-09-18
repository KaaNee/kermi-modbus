"""Puffer-/Kühlpufferspeicher block (project plan §5.2, addresses 1-2, 50-51)."""

from __future__ import annotations

from modbus_connection.model import Component, gauge

from .. import const


class Buffer(Component):
    """Heating buffer tank temperatures. Call ``async_update()`` to refresh."""

    actual_temperature = gauge(const.STORAGE_BUFFER_ACTUAL_TEMPERATURE.address, const.STORAGE_BUFFER_ACTUAL_TEMPERATURE.scale, signed=True, unit="°C")
    target_temperature = gauge(const.STORAGE_BUFFER_TARGET_TEMPERATURE.address, const.STORAGE_BUFFER_TARGET_TEMPERATURE.scale, signed=True, unit="°C")


class CoolingBuffer(Component):
    """Cooling buffer tank temperatures. Call ``async_update()`` to refresh."""

    actual_temperature = gauge(const.STORAGE_COOLING_BUFFER_ACTUAL_TEMPERATURE.address, const.STORAGE_COOLING_BUFFER_ACTUAL_TEMPERATURE.scale, signed=True, unit="°C")
    target_temperature = gauge(const.STORAGE_COOLING_BUFFER_TARGET_TEMPERATURE.address, const.STORAGE_COOLING_BUFFER_TARGET_TEMPERATURE.scale, signed=True, unit="°C")
