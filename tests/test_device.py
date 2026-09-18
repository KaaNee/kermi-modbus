"""Tests for KermiDevice: wiring an x-center unit together with the optional,
independent heating-circuit (unit 50) and DHW (unit 51) storage modules.
"""

from __future__ import annotations

from modbus_connection.mock import MockModbusConnection

from kermi_modbus import KermiDevice
from kermi_modbus.models import XChangeDynamicProProfile


def _make_units(*unit_ids: int):
    conn = MockModbusConnection()
    return tuple(conn.for_unit(unit_id) for unit_id in unit_ids)


async def test_device_defaults_to_x_change_dynamic_pro_profile() -> None:
    (xcenter_unit,) = _make_units(40)
    device = KermiDevice(xcenter_unit)
    assert isinstance(device.profile, XChangeDynamicProProfile)


async def test_device_with_no_storage_modules() -> None:
    (xcenter_unit,) = _make_units(40)
    device = KermiDevice(xcenter_unit)
    assert device.heating_circuit_module is None
    assert device.dhw_module is None


async def test_device_wires_heating_circuit_and_dhw_modules_independently() -> None:
    """CONFIRMED against real hardware (project plan §10.1): 50 and 51 are
    functionally SEPARATE modules — 50 owns the heating-circuit domain, 51
    owns DHW. Seed both units with both domains' registers and assert each
    module only reflects its own domain, proving the split isn't just two
    independent objects that happen to read the same full register set.
    """
    xcenter_unit, unit_50, unit_51 = _make_units(40, 50, 51)
    for unit in (unit_50, unit_51):
        unit.holding[150] = 1  # heating circuit status: Heating
        unit.holding[100] = 485  # DHW actual temperature: 48.5 °C

    device = KermiDevice(xcenter_unit, heating_circuit_unit=unit_50, dhw_unit=unit_51)
    await device.async_update()

    assert device.heating_circuit_module.heating_circuit.status.name == "HEATING"
    assert device.dhw_module.dhw.actual_temperature == 48.5

    # The heating-circuit module has no DHW attribute and vice versa — the
    # domain split is structural, not just which fields happen to be read.
    assert not hasattr(device.heating_circuit_module, "dhw")
    assert not hasattr(device.dhw_module, "heating_circuit")
