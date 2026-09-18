"""Heizkreis block (project plan §5.2, addresses 150-163).

Numeric writable registers (parallel shift, summer/winter/cooling
thresholds) get a range validator built from the Excel's documented
Min/Max — see validation.py. Enum-typed writable registers (operating_type,
energy_mode, manual_season_selection) do not: their Python enum type
already constrains valid values, so a second numeric range check would be
redundant.
"""

from __future__ import annotations

from modbus_connection.model import Component, enum, gauge, integer

from .. import const
from ..enums import EnergyMode, HeatingCircuitStatus, OperatingMode, OperatingType, SeasonSelection
from ..validation import range_validator


class HeatingCircuit(Component):
    """Heating circuit status, temperatures, and control settings.

    Call ``async_update()`` to refresh.
    """

    status = enum(const.STORAGE_HEATING_CIRCUIT_STATUS.address, HeatingCircuitStatus, signed=False)
    actual_temperature = gauge(const.STORAGE_HEATING_CIRCUIT_ACTUAL_TEMPERATURE.address, const.STORAGE_HEATING_CIRCUIT_ACTUAL_TEMPERATURE.scale, signed=True, unit="°C")
    # Read-only despite carrying a documented range (see const.py) —
    # deliberately not ``writable``.
    target_temperature = gauge(const.STORAGE_HEATING_CIRCUIT_TARGET_TEMPERATURE.address, const.STORAGE_HEATING_CIRCUIT_TARGET_TEMPERATURE.scale, signed=True, unit="°C")
    operating_mode = enum(const.STORAGE_OPERATING_MODE.address, OperatingMode, signed=False)
    operating_type = enum(const.STORAGE_OPERATING_TYPE.address, OperatingType, signed=False, writable=True)
    energy_mode = enum(const.STORAGE_ENERGY_MODE.address, EnergyMode, signed=False, writable=True)
    # Signed! See const.py — the one field where an unsigned read would
    # silently misdecode negative values.
    heating_curve_parallel_shift = integer(
        const.STORAGE_HEATING_CURVE_PARALLEL_SHIFT.address,
        signed=True,
        writable=range_validator(const.STORAGE_HEATING_CURVE_PARALLEL_SHIFT),
    )
    manual_season_selection = enum(
        const.STORAGE_MANUAL_SEASON_SELECTION.address, SeasonSelection, signed=False, writable=True
    )
    summer_mode_off_threshold = gauge(
        const.STORAGE_SUMMER_MODE_OFF_THRESHOLD.address,
        const.STORAGE_SUMMER_MODE_OFF_THRESHOLD.scale,
        signed=True,
        unit="°C",
        writable=range_validator(const.STORAGE_SUMMER_MODE_OFF_THRESHOLD),
    )
    winter_mode_on_threshold = gauge(
        const.STORAGE_WINTER_MODE_ON_THRESHOLD.address,
        const.STORAGE_WINTER_MODE_ON_THRESHOLD.scale,
        signed=True,
        unit="°C",
        writable=range_validator(const.STORAGE_WINTER_MODE_ON_THRESHOLD),
    )
    cooling_mode_on_threshold = gauge(
        const.STORAGE_COOLING_MODE_ON_THRESHOLD.address,
        const.STORAGE_COOLING_MODE_ON_THRESHOLD.scale,
        signed=True,
        unit="°C",
        writable=range_validator(const.STORAGE_COOLING_MODE_ON_THRESHOLD),
    )
    cooling_mode_off_threshold = gauge(
        const.STORAGE_COOLING_MODE_OFF_THRESHOLD.address,
        const.STORAGE_COOLING_MODE_OFF_THRESHOLD.scale,
        signed=True,
        unit="°C",
        writable=range_validator(const.STORAGE_COOLING_MODE_OFF_THRESHOLD),
    )
    summer_mode_active = integer(const.STORAGE_SUMMER_MODE_ACTIVE.address, signed=False)
    cooling_mode_active = integer(const.STORAGE_COOLING_MODE_ACTIVE.address, signed=False)
