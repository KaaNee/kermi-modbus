"""Trinkwassererwärmung (DHW) block (project plan §5.2, addresses 100-104)."""

from __future__ import annotations

from modbus_connection.model import Component, gauge, integer

from .. import const
from ..validation import range_validator


class DomesticHotWater(Component):
    """DHW temperatures + setpoints. Call ``async_update()`` to refresh."""

    actual_temperature = gauge(const.STORAGE_DHW_ACTUAL_TEMPERATURE.address, const.STORAGE_DHW_ACTUAL_TEMPERATURE.scale, signed=True, unit="°C")
    target_temperature = gauge(const.STORAGE_DHW_TARGET_TEMPERATURE.address, const.STORAGE_DHW_TARGET_TEMPERATURE.scale, signed=True, unit="°C")
    constant_setpoint = gauge(
        const.STORAGE_DHW_CONSTANT_SETPOINT.address,
        const.STORAGE_DHW_CONSTANT_SETPOINT.scale,
        signed=True,
        unit="°C",
        writable=range_validator(const.STORAGE_DHW_CONSTANT_SETPOINT),
    )
    # Plain 0/1 register (see const.py — the real production YAML had the
    # wrong max_value here, a likely copy-paste bug; corrected in this
    # library).
    single_charge = integer(
        const.STORAGE_DHW_SINGLE_CHARGE.address,
        signed=False,
        writable=range_validator(const.STORAGE_DHW_SINGLE_CHARGE),
    )
    single_charge_setpoint = gauge(
        const.STORAGE_DHW_SINGLE_CHARGE_SETPOINT.address,
        const.STORAGE_DHW_SINGLE_CHARGE_SETPOINT.scale,
        signed=True,
        unit="°C",
        writable=range_validator(const.STORAGE_DHW_SINGLE_CHARGE_SETPOINT),
    )
