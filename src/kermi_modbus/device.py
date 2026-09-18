"""Top-level Kermi device objects.

Two Modbus units, not one — this is the structural difference from
``e3dc-modbus`` (see project plan §3): the x-center (heat pump controller)
and the storage module answer on separate unit IDs, and the real production
installation this library was built against reads from both concurrently
(DHW registers from unit 51, heating-circuit/status registers from unit 50).

CONFIRMED against real hardware (project plan §10.1, 2026-09-11): 50 and 51
are functionally SEPARATE modules, not one module answering identically on
both IDs. Unit 50 owns the heating-circuit domain, unit 51 owns DHW — a read
on the "wrong" unit doesn't error, it silently returns 0 / a default value
(no address validation against the instance). The library reflects this
split directly: ``KermiHeatingCircuitModule`` (unit 50) exposes only the
heating-circuit-domain registers (buffer, cooling buffer, heating circuit,
external heat generator for heating, sensors, work hours), and
``KermiDhwModule`` (unit 51) exposes only the DHW-domain registers (DHW,
external heat generator for DHW). ``KermiDevice`` takes each as an optional,
independently-configurable unit — an installation may have either, both, or
neither.

No ``async_probe()`` classmethod (unlike ``E3DCDevice``): Kermi's register
list documents no model/serial identification register anywhere, so there
is nothing to read that would confirm which model is connected — see
``models/_base.py``. Construct ``KermiDevice`` directly with an explicit
profile (default: the one verified profile, x-change dynamic pro).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from modbus_connection.model import ComponentGroup

from .models import KermiModelProfile, XChangeDynamicProProfile
from .storage_module import (
    Buffer,
    CoolingBuffer,
    DomesticHotWater,
    ExternalHeatGeneratorDhw,
    ExternalHeatGeneratorHeating,
    HeatingCircuit,
    Sensors,
)
from .storage_module import WorkHours as StorageWorkHours
from .xcenter import Alarm, ChargingCircuit, EnergySource, Power, PvModulation, State
from .xcenter import WorkHours as XCenterWorkHours

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit


class KermiXCenter:
    """The x-center / x-change dynamic pro controller (unit ID 40, cascade
    slaves 41/42, ...).

    PV-modulation (addresses 300-303) is opt-in and off by default: the
    reference openHAB binding disables it by default too, and the device's
    own documentation warns against polling too aggressively (see project
    plan §8) — reading an extra block should be a deliberate choice, not the
    default.
    """

    def __init__(self, unit: ModbusUnit, *, include_pv_modulation: bool = False) -> None:
        self._unit = unit
        self.energy_source = EnergySource(unit)
        self.charging_circuit = ChargingCircuit(unit)
        self.power = Power(unit)
        self.work_hours = XCenterWorkHours(unit)
        self.state = State(unit)
        self.alarm = Alarm(unit)
        self.pv_modulation = PvModulation(unit) if include_pv_modulation else None

        components = [
            self.energy_source,
            self.charging_circuit,
            self.power,
            self.work_hours,
            self.state,
            self.alarm,
        ]
        if self.pv_modulation is not None:
            components.append(self.pv_modulation)
        self._group = ComponentGroup(unit, components)

    async def async_update(self) -> None:
        """Refresh every x-center subsystem in as few Modbus requests as possible."""
        await self._group.async_update()


class KermiHeatingCircuitModule:
    """Speichersystemmodul, Heizkreis-Domäne (unit ID 50, see module docstring)."""

    def __init__(self, unit: ModbusUnit) -> None:
        self._unit = unit
        self.buffer = Buffer(unit)
        self.cooling_buffer = CoolingBuffer(unit)
        self.heating_circuit = HeatingCircuit(unit)
        self.external_heat_generator = ExternalHeatGeneratorHeating(unit)
        self.sensors = Sensors(unit)
        self.work_hours = StorageWorkHours(unit)

        self._group = ComponentGroup(
            unit,
            [
                self.buffer,
                self.cooling_buffer,
                self.heating_circuit,
                self.external_heat_generator,
                self.sensors,
                self.work_hours,
            ],
        )

    async def async_update(self) -> None:
        """Refresh every heating-circuit subsystem in as few Modbus requests as possible."""
        await self._group.async_update()


class KermiDhwModule:
    """Speichersystemmodul, TWE-Domäne (unit ID 51, see module docstring)."""

    def __init__(self, unit: ModbusUnit) -> None:
        self._unit = unit
        self.dhw = DomesticHotWater(unit)
        self.external_heat_generator = ExternalHeatGeneratorDhw(unit)

        self._group = ComponentGroup(unit, [self.dhw, self.external_heat_generator])

    async def async_update(self) -> None:
        """Refresh every DHW subsystem in as few Modbus requests as possible."""
        await self._group.async_update()


class KermiDevice:
    """A Kermi heat pump installation: one x-center + optional heating-circuit
    and/or DHW storage modules.
    """

    def __init__(
        self,
        xcenter_unit: ModbusUnit,
        *,
        heating_circuit_unit: ModbusUnit | None = None,
        dhw_unit: ModbusUnit | None = None,
        profile: KermiModelProfile | None = None,
        include_pv_modulation: bool = False,
    ) -> None:
        self.profile = profile or XChangeDynamicProProfile()
        self.xcenter = KermiXCenter(xcenter_unit, include_pv_modulation=include_pv_modulation)
        self.heating_circuit_module = (
            KermiHeatingCircuitModule(heating_circuit_unit) if heating_circuit_unit is not None else None
        )
        self.dhw_module = KermiDhwModule(dhw_unit) if dhw_unit is not None else None

    async def async_update(self) -> None:
        """Refresh the x-center and every configured storage module concurrently."""
        tasks = [self.xcenter.async_update()]
        if self.heating_circuit_module is not None:
            tasks.append(self.heating_circuit_module.async_update())
        if self.dhw_module is not None:
            tasks.append(self.dhw_module.async_update())
        await asyncio.gather(*tasks)
