"""kermi-modbus — read and write a Kermi heat pump over Modbus TCP.

Construct ``KermiDevice(xcenter_unit, heating_circuit_unit=..., dhw_unit=...)``
with ``modbus_connection.ModbusUnit`` objects, call
``await device.async_update()``, then read its subsystems as normal Python
objects::

    device.xcenter.power.cop
    device.xcenter.charging_circuit.flow_temperature
    device.dhw_module.dhw.actual_temperature
    device.heating_circuit_module.heating_circuit.status

Both storage-module arguments are optional and independent (project plan
§10.1: unit 50 = Heizkreis, unit 51 = TWE — two functionally separate
modules, not one module on two IDs). See device.py for why there are three
kinds of unit and no ``async_probe()`` — unlike ``e3dc-modbus``, Kermi
documents no model-identification register to probe.
"""

from __future__ import annotations

from .device import KermiDevice, KermiDhwModule, KermiHeatingCircuitModule, KermiXCenter
from .enums import (
    EnergyMode,
    ExternalHeatGeneratorMode,
    ExternalHeatGeneratorStatus,
    GlobalState,
    HeatingCircuitStatus,
    OperatingMode,
    OperatingType,
    SeasonSelection,
)
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
from .xcenter import Alarm, ChargingCircuit, EnergySource, Power, PvModulation, State

__all__ = [
    "Alarm",
    "Buffer",
    "ChargingCircuit",
    "CoolingBuffer",
    "DomesticHotWater",
    "EnergyMode",
    "EnergySource",
    "ExternalHeatGeneratorDhw",
    "ExternalHeatGeneratorHeating",
    "ExternalHeatGeneratorMode",
    "ExternalHeatGeneratorStatus",
    "GlobalState",
    "HeatingCircuit",
    "HeatingCircuitStatus",
    "KermiDevice",
    "KermiDhwModule",
    "KermiHeatingCircuitModule",
    "KermiModelProfile",
    "KermiXCenter",
    "OperatingMode",
    "OperatingType",
    "Power",
    "PvModulation",
    "SeasonSelection",
    "Sensors",
    "State",
    "XChangeDynamicProProfile",
]
