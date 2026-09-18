"""Tests for KermiHeatingCircuitModule (unit 50), against modbus_connection's
in-memory mock backend (no physical device needed).
"""

from __future__ import annotations

from modbus_connection.mock import MockModbusConnection

from kermi_modbus import EnergyMode, HeatingCircuitStatus
from kermi_modbus.device import KermiHeatingCircuitModule


def _make_unit(unit_id: int = 50):
    conn = MockModbusConnection()
    return conn.for_unit(unit_id)


async def test_heating_circuit_status_zero_is_off_not_unknown() -> None:
    """Regression test for the real production `nan_value: 0` bug (see
    project plan §4) applied to the storage module's own status register.
    """
    unit = _make_unit()
    unit.holding[150] = 0

    module = KermiHeatingCircuitModule(unit)
    await module.async_update()

    assert module.heating_circuit.status is HeatingCircuitStatus.OFF


async def test_energy_mode_default_is_normal_not_unknown() -> None:
    unit = _make_unit()
    unit.holding[155] = 2

    module = KermiHeatingCircuitModule(unit)
    await module.async_update()

    assert module.heating_circuit.energy_mode is EnergyMode.NORMAL


async def test_heating_curve_parallel_shift_decodes_negative_value() -> None:
    """Regression test for the signed-vs-unsigned decode bug found in the
    reference openHAB binding (project plan §6.1): a negative parallel
    shift must not be misread as a large positive number.
    """
    unit = _make_unit()
    unit.holding[156] = (-3) & 0xFFFF  # -3, two's complement

    module = KermiHeatingCircuitModule(unit)
    await module.async_update()

    assert module.heating_circuit.heating_curve_parallel_shift == -3


async def test_outside_temperature_averaged_decodes() -> None:
    unit = _make_unit()
    unit.holding[255] = 117  # 11.7 °C — matches real production value

    module = KermiHeatingCircuitModule(unit)
    await module.async_update()

    assert module.sensors.outside_temperature_averaged == 11.7


async def test_ext_heat_generator_status_gap_value_decodes_as_none() -> None:
    """ExternalHeatGeneratorStatus is sparse (0, 100, 200-209, 300-309) —
    a raw value in one of the large gaps (e.g. 150) must decode as ``None``
    without raising, not crash the whole storage-module read.
    """
    from kermi_modbus.storage_module import ExternalHeatGeneratorHeating

    unit = _make_unit()
    unit.holding[200] = 150  # inside a documented gap

    block = ExternalHeatGeneratorHeating(unit)
    await block.async_update()  # must not raise

    assert block.status is None
