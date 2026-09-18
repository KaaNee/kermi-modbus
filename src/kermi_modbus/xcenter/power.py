"""Leistung und Effizienz block (project plan §5.1, x-center addresses 100-111).

See const.py for the electric-power scale-factor note (address 108 — the
real production YAML was missing this scale, not the register itself).
"""

from __future__ import annotations

from modbus_connection.model import Component, gauge

from .. import const


class Power(Component):
    """COP + thermal + electric power. Call ``async_update()`` to refresh."""

    cop = gauge(const.XCENTER_COP.address, const.XCENTER_COP.scale, signed=False)
    cop_heating = gauge(const.XCENTER_COP_HEATING.address, const.XCENTER_COP_HEATING.scale, signed=False)
    cop_dhw = gauge(const.XCENTER_COP_DHW.address, const.XCENTER_COP_DHW.scale, signed=False)
    cop_cooling = gauge(const.XCENTER_COP_COOLING.address, const.XCENTER_COP_COOLING.scale, signed=False)

    power = gauge(const.XCENTER_POWER.address, const.XCENTER_POWER.scale, signed=False, unit="kW")
    power_heating = gauge(const.XCENTER_POWER_HEATING.address, const.XCENTER_POWER_HEATING.scale, signed=False, unit="kW")
    power_dhw = gauge(const.XCENTER_POWER_DHW.address, const.XCENTER_POWER_DHW.scale, signed=False, unit="kW")
    power_cooling = gauge(const.XCENTER_POWER_COOLING.address, const.XCENTER_POWER_COOLING.scale, signed=False, unit="kW")

    electric_power = gauge(const.XCENTER_ELECTRIC_POWER.address, const.XCENTER_ELECTRIC_POWER.scale, signed=False, unit="kW")
    electric_power_heating = gauge(const.XCENTER_ELECTRIC_POWER_HEATING.address, const.XCENTER_ELECTRIC_POWER_HEATING.scale, signed=False, unit="kW")
    electric_power_dhw = gauge(const.XCENTER_ELECTRIC_POWER_DHW.address, const.XCENTER_ELECTRIC_POWER_DHW.scale, signed=False, unit="kW")
    electric_power_cooling = gauge(const.XCENTER_ELECTRIC_POWER_COOLING.address, const.XCENTER_ELECTRIC_POWER_COOLING.scale, signed=False, unit="kW")
