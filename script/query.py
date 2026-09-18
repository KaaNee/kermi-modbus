#!/usr/bin/env python
"""Query a Kermi heat pump over Modbus TCP without Home Assistant.

The x-center and the storage module(s) sit behind the same Modbus TCP
endpoint, distinguished only by unit/slave ID — not separate hosts (this
matches the real production ``modbus.yaml``, which uses one ``host:port``
with a ``device_address`` per sensor). Connect once, then request one
``ModbusUnit`` per unit ID.

CONFIRMED against real hardware (project plan §10.1): unit 50 and unit 51 are
functionally SEPARATE modules, not one module answering on both IDs — 50
owns the heating-circuit domain, 51 owns DHW. Pass whichever unit ID(s) your
installation actually has.

Usage:
    python script/query.py 192.168.1.50 --xcenter-unit 40 --heating-circuit-unit 50 --dhw-unit 51
"""

from __future__ import annotations

import argparse
import asyncio


async def _test_pv_setpoint_writes(xcenter_unit) -> None:
    """Round-trip write test for the two PV-modulation setpoints (302/303).

    Deliberately conservative (project plan §12: test write paths against
    UNCRITICAL registers first, 302/303 before 201/203 — these two only
    affect behaviour during actual PV surplus, not the core heating/DHW
    control that 201/203 govern): read the real current setpoints, write a
    +1.0°C test value, read back to confirm the write actually reached the
    device (not just a local cache), then unconditionally restore the
    original values — in a ``finally`` block, so a failure partway through
    still leaves the device the way it was found, not mid-test.
    """
    from kermi_modbus.xcenter.pv_modulation import PvModulation

    print("\n--- PV setpoint write test (x-center, addresses 302/303) ---")
    pv = PvModulation(xcenter_unit)
    await pv.async_update()
    original_heating = pv.target_temperature_heating
    original_dhw = pv.target_temperature_dhw
    print(f"Original: heating={original_heating} °C, dhw={original_dhw} °C")

    test_heating = round(original_heating + 1.0, 1)
    test_dhw = round(original_dhw + 1.0, 1)

    try:
        await pv.write("target_temperature_heating", test_heating)
        await pv.write("target_temperature_dhw", test_dhw)

        readback = PvModulation(xcenter_unit)
        await readback.async_update()
        write_ok = (
            readback.target_temperature_heating == test_heating
            and readback.target_temperature_dhw == test_dhw
        )
        print(
            f"After write: heating={readback.target_temperature_heating} °C "
            f"(expected {test_heating}), dhw={readback.target_temperature_dhw} °C "
            f"(expected {test_dhw}) -> write_verified={write_ok}"
        )
    finally:
        await pv.write("target_temperature_heating", original_heating)
        await pv.write("target_temperature_dhw", original_dhw)

        restored = PvModulation(xcenter_unit)
        await restored.async_update()
        restore_ok = (
            restored.target_temperature_heating == original_heating
            and restored.target_temperature_dhw == original_dhw
        )
        print(
            f"Restored: heating={restored.target_temperature_heating} °C, "
            f"dhw={restored.target_temperature_dhw} °C -> restore_verified={restore_ok}"
        )


async def _test_external_heat_generator_mode_write(component, label: str) -> None:
    """Round-trip write test for an external-heat-generator mode register
    (201 = heating, 203 = DHW — project plan §12, the highest-impact write
    registers, tested last and deliberately).

    Conservative in the choice of test value: only ever toggles between
    ``AUTO`` and ``HEAT_PUMP_ONLY``, both of which keep the heat pump itself
    active as a source. Never writes ``SECONDARY_HEAT_GENERATOR_ONLY`` (3),
    which would take the heat pump out of the loop entirely — an
    unnecessary risk for a few seconds of write verification. If the
    device's current mode is already outside this safe pair (``BOTH`` or
    ``SECONDARY_HEAT_GENERATOR_ONLY``), skip rather than guess a safe
    round trip.
    """
    from kermi_modbus.enums import ExternalHeatGeneratorMode

    print(f"\n--- {label} mode write test ---")
    await component.async_update()
    original = component.mode
    print(f"Original: {original.name if original is not None else original}")

    safe_pair = {ExternalHeatGeneratorMode.AUTO, ExternalHeatGeneratorMode.HEAT_PUMP_ONLY}
    if original not in safe_pair:
        print(
            f"SKIPPED: original mode {original!r} is outside the conservative "
            "AUTO/HEAT_PUMP_ONLY test set — not touching it."
        )
        return

    test_value = (
        ExternalHeatGeneratorMode.HEAT_PUMP_ONLY
        if original is ExternalHeatGeneratorMode.AUTO
        else ExternalHeatGeneratorMode.AUTO
    )

    try:
        await component.write("mode", test_value)
        await component.async_update()
        write_ok = component.mode is test_value
        print(f"After write: {component.mode.name} (expected {test_value.name}) -> write_verified={write_ok}")
    finally:
        await component.write("mode", original)
        await component.async_update()
        restore_ok = component.mode is original
        print(f"Restored: {component.mode.name} -> restore_verified={restore_ok}")


async def _run(
    host: str,
    port: int,
    xcenter_unit_id: int,
    heating_circuit_unit_id: int | None,
    dhw_unit_id: int | None,
    test_pv_write: bool,
    test_ext_heat_generator_mode_write: bool,
) -> None:
    from modbus_connection.tmodbus import connect_tcp

    from kermi_modbus import KermiDevice

    # Kermi speaks native Modbus TCP (MBAP framing); a Modbus TCP link is
    # always MBAP-framed, so the framer argument is deprecated and omitted.
    connection = await connect_tcp(host, port=port)
    try:
        xcenter_unit = connection.for_unit(xcenter_unit_id)
        heating_circuit_unit = (
            connection.for_unit(heating_circuit_unit_id) if heating_circuit_unit_id is not None else None
        )
        dhw_unit = connection.for_unit(dhw_unit_id) if dhw_unit_id is not None else None

        if test_pv_write:
            await _test_pv_setpoint_writes(xcenter_unit)

        device = KermiDevice(xcenter_unit, heating_circuit_unit=heating_circuit_unit, dhw_unit=dhw_unit)
        await device.async_update()

        if test_ext_heat_generator_mode_write:
            if device.heating_circuit_module is not None:
                await _test_external_heat_generator_mode_write(
                    device.heating_circuit_module.external_heat_generator, "Heating (register 201)"
                )
            if device.dhw_module is not None:
                await _test_external_heat_generator_mode_write(
                    device.dhw_module.external_heat_generator, "DHW (register 203)"
                )

        state_name = (
            device.xcenter.state.global_state.name
            if device.xcenter.state.global_state is not None
            else "UNDOCUMENTED (raw value not in GlobalState enum)"
        )
        print(f"Global state:     {state_name}")
        print(f"Alarm active:     {bool(device.xcenter.alarm.active)}")
        print(f"COP:              {device.xcenter.power.cop}")
        print(f"Power:            {device.xcenter.power.power} kW")
        print(f"Electric power:   {device.xcenter.power.electric_power} kW")
        print(f"Flow temperature: {device.xcenter.charging_circuit.flow_temperature} °C")
        print(f"Outside temp.:    {device.xcenter.energy_source.outside_temperature} °C")

        # Work-hours factor check (project plan §6.1/§9): the Excel documents
        # a 0.1 h scale here, which caps a uint16 at ~9 months of runtime —
        # implausible for a device installed since 2023. Print BOTH the raw
        # register (no scale applied) and the library's currently-assumed
        # decoded value (raw * 0.1), so the two can be compared against the
        # device's actual known runtime.
        raw_compressor_hours = (await xcenter_unit.read_holding_registers(152, 1))[0]
        print(f"\n--- Work hours (x-center, unit {xcenter_unit_id}) ---")
        print(f"Compressor (raw register 152, no scale): {raw_compressor_hours}")
        print(f"Compressor (decoded, current 0.1 factor): {device.xcenter.work_hours.compressor} h")
        print(f"Fan (decoded, current 0.1 factor):        {device.xcenter.work_hours.fan} h")
        print(f"Storage loading pump (decoded, 0.1):      {device.xcenter.work_hours.storage_loading_pump} h")

        if device.heating_circuit_module is not None:
            module = device.heating_circuit_module
            print(f"\n--- Heating-circuit module (unit {heating_circuit_unit_id}) ---")
            print(f"Heating circuit status: {module.heating_circuit.status.name}")
            print(f"Outside temp. (avg):    {module.sensors.outside_temperature_averaged} °C")
            print(f"Heating circuit pump workhours: {module.work_hours.heating_circuit_pump} h (raw, undisputed)")
            print(f"Heating rod workhours:          {module.work_hours.heating_rod} h (raw, undisputed)")

        if device.dhw_module is not None:
            module = device.dhw_module
            print(f"\n--- DHW module (unit {dhw_unit_id}) ---")
            print(f"DHW actual/target: {module.dhw.actual_temperature} / {module.dhw.target_temperature} °C")
    finally:
        await connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="Kermi Modbus TCP gateway IP address or hostname")
    parser.add_argument("--port", type=int, default=502, help="Modbus TCP port (default: 502)")
    parser.add_argument("--xcenter-unit", type=int, default=40, help="x-center unit/slave ID (default: 40)")
    parser.add_argument(
        "--heating-circuit-unit",
        type=int,
        default=None,
        help="Heating-circuit storage-module unit/slave ID (project plan §10.1, typically 50). Omit to skip.",
    )
    parser.add_argument(
        "--dhw-unit",
        type=int,
        default=None,
        help="DHW storage-module unit/slave ID (project plan §10.1, typically 51). Omit to skip.",
    )
    parser.add_argument(
        "--test-pv-write",
        action="store_true",
        help=(
            "Round-trip write test on the PV-modulation setpoints (addresses 302/303): "
            "read current values, write +1.0°C, read back to verify, then restore the "
            "original values (see project plan §12 — the deliberately uncritical register "
            "pair to test writes against first). Off by default."
        ),
    )
    parser.add_argument(
        "--test-ext-heat-generator-mode-write",
        action="store_true",
        help=(
            "Round-trip write test on the external-heat-generator mode registers "
            "(201 heating / 203 DHW, needs --heating-circuit-unit / --dhw-unit): "
            "conservatively toggles only between AUTO and HEAT_PUMP_ONLY, then restores "
            "the original value (see project plan §12 — the highest-impact write "
            "registers, tested last). Off by default."
        ),
    )
    args = parser.parse_args()

    asyncio.run(
        _run(
            args.host,
            args.port,
            args.xcenter_unit,
            args.heating_circuit_unit,
            args.dhw_unit,
            args.test_pv_write,
            args.test_ext_heat_generator_mode_write,
        )
    )


if __name__ == "__main__":
    main()
