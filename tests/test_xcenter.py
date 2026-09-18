"""Tests for KermiXCenter, against modbus_connection's in-memory mock backend
(no physical device needed — see modbus_connection.mock.MockModbusConnection).
"""

from __future__ import annotations

from modbus_connection.mock import MockModbusConnection

from kermi_modbus import GlobalState
from kermi_modbus.device import KermiXCenter


def _make_unit(unit_id: int = 40):
    conn = MockModbusConnection()
    return conn.for_unit(unit_id)


async def test_power_block_decodes_scaled_int16_values() -> None:
    unit = _make_unit()
    unit.holding[100] = 35  # COP 3.5, scale 0.1
    unit.holding[104] = 82  # power 8.2 kW, scale 0.1
    unit.holding[108] = 21  # electric power 2.1 kW, scale 0.1

    xcenter = KermiXCenter(unit)
    await xcenter.async_update()

    assert xcenter.power.cop == 3.5
    assert xcenter.power.power == 8.2
    assert xcenter.power.electric_power == 2.1


async def test_global_state_zero_is_standby_not_unknown() -> None:
    """Regression test for the real production `nan_value: 0` bug (see
    project plan §4): a global state of 0 (Standby) must decode as the
    ``GlobalState.STANDBY`` enum member, never as a missing/None value.
    """
    unit = _make_unit()
    unit.holding[200] = 0

    xcenter = KermiXCenter(unit)
    await xcenter.async_update()

    assert xcenter.state.global_state is GlobalState.STANDBY


async def test_global_state_decodes_documented_values() -> None:
    unit = _make_unit()
    unit.holding[200] = 4  # Heating

    xcenter = KermiXCenter(unit)
    await xcenter.async_update()

    assert xcenter.state.global_state is GlobalState.HEATING


async def test_pv_modulation_excluded_by_default() -> None:
    unit = _make_unit()
    xcenter = KermiXCenter(unit)
    assert xcenter.pv_modulation is None


async def test_pv_modulation_included_when_requested() -> None:
    unit = _make_unit()
    unit.holding[301] = 150  # 15.0 W, scale 0.1
    unit.holding[302] = 500  # 50.0 °C, scale 0.1

    xcenter = KermiXCenter(unit, include_pv_modulation=True)
    await xcenter.async_update()

    assert xcenter.pv_modulation is not None
    assert xcenter.pv_modulation.power == 15.0
    assert xcenter.pv_modulation.target_temperature_heating == 50.0


async def test_charging_circuit_decodes_negative_temperature() -> None:
    """Signed decode check: below-freezing outdoor/return temperatures must
    not wrap around as large positive values.
    """
    unit = _make_unit()
    unit.holding[51] = (-50) & 0xFFFF  # -5.0 °C, scale 0.1, two's complement

    xcenter = KermiXCenter(unit)
    await xcenter.async_update()

    assert xcenter.charging_circuit.return_temperature == -5.0


async def test_global_state_decodes_undocumented_value_as_none() -> None:
    """The Excel documents GlobalState 0-9 but states max_value=10 (its own
    off-by-one, see const.py) — verify an out-of-range raw value does not
    crash the whole block read. modbus_connection's enum() field decodes an
    unmapped value as ``None`` (logging a warning) rather than raising; this
    matters far more for the sparse ExternalHeatGeneratorStatus enum (see
    test_storage_module.py) than for this dense one, but the behaviour is
    the same code path.
    """
    unit = _make_unit()
    unit.holding[200] = 10  # documented as "Max", but not a named state

    xcenter = KermiXCenter(unit)
    await xcenter.async_update()  # must not raise

    assert xcenter.state.global_state is None
