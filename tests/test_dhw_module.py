"""Tests for KermiDhwModule (unit 51), against modbus_connection's in-memory
mock backend (no physical device needed).
"""

from __future__ import annotations

from modbus_connection.mock import MockModbusConnection

from kermi_modbus.device import KermiDhwModule


def _make_unit(unit_id: int = 51):
    conn = MockModbusConnection()
    return conn.for_unit(unit_id)


async def test_dhw_decodes_scaled_temperatures() -> None:
    unit = _make_unit()
    unit.holding[100] = 485  # 48.5 °C, scale 0.1 — matches real production value
    unit.holding[101] = 500  # 50.0 °C

    module = KermiDhwModule(unit)
    await module.async_update()

    assert module.dhw.actual_temperature == 48.5
    assert module.dhw.target_temperature == 50.0


async def test_ext_heat_generator_dhw_status_gap_value_decodes_as_none() -> None:
    """ExternalHeatGeneratorStatus is sparse (0, 100, 200-209, 300-309) —
    a raw value in one of the large gaps (e.g. 150) must decode as ``None``
    without raising, not crash the whole DHW-module read.
    """
    from kermi_modbus.storage_module import ExternalHeatGeneratorDhw

    unit = _make_unit()
    unit.holding[202] = 150  # inside a documented gap

    block = ExternalHeatGeneratorDhw(unit)
    await block.async_update()  # must not raise

    assert block.status is None
