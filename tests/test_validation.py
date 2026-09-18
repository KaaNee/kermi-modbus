"""Tests for validation.range_validator: does a write out-of-documented-range
actually get rejected before reaching the device, and an in-range write
actually succeed?

This exercises the real write path (Component.write -> field.writable(value)
-> modbus_connection's write logic -> the mock's holding registers), not
just the validator function in isolation — see project plan §12: write
paths on real heating control are the top risk, and an untested validator
is not meaningfully safer than no validator at all.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusConnection

from kermi_modbus.storage_module import DomesticHotWater, HeatingCircuit
from kermi_modbus.validation import KermiValueError


def _make_unit(unit_id: int = 51):
    conn = MockModbusConnection()
    return conn.for_unit(unit_id)


async def test_dhw_constant_setpoint_rejects_out_of_range_write() -> None:
    unit = _make_unit()
    dhw = DomesticHotWater(unit)

    with pytest.raises(KermiValueError):
        await dhw.write("constant_setpoint", 500)  # documented range: 0-85 °C

    # Rejected before it ever reached the device.
    assert unit.holding.get(102) is None


async def test_dhw_constant_setpoint_accepts_in_range_write() -> None:
    unit = _make_unit()
    dhw = DomesticHotWater(unit)

    await dhw.write("constant_setpoint", 55)  # within 0-85 °C

    dhw2 = DomesticHotWater(unit)
    await dhw2.async_update()
    assert dhw2.constant_setpoint == 55.0


async def test_heating_curve_parallel_shift_rejects_out_of_range_write() -> None:
    unit = _make_unit(50)
    circuit = HeatingCircuit(unit)

    with pytest.raises(KermiValueError):
        await circuit.write("heating_curve_parallel_shift", 6)  # documented range: -5..5


async def test_heating_curve_parallel_shift_accepts_boundary_value() -> None:
    unit = _make_unit(50)
    circuit = HeatingCircuit(unit)

    await circuit.write("heating_curve_parallel_shift", -5)  # boundary, must be accepted

    circuit2 = HeatingCircuit(unit)
    await circuit2.async_update()
    assert circuit2.heating_curve_parallel_shift == -5
