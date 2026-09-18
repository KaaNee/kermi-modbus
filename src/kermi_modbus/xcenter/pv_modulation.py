"""PV Modulation Wärmepumpe block (project plan §5.1, x-center addresses 300-303).

Disabled by default in the real-world reference (openHAB's binding has a
``pvEnabled`` option, default ``false``, and the x-center's own README warns
against polling too aggressively) — see project plan §8. Callers should make
reading this block opt-in, not read it unconditionally alongside the other
blocks.
"""

from __future__ import annotations

from modbus_connection.model import Component, gauge, integer

from .. import const


class PvModulation(Component):
    """PV-surplus modulation state + setpoints. Call ``async_update()`` to refresh."""

    active = integer(const.XCENTER_PV_MODULATION_ACTIVE.address, signed=False)
    power = gauge(const.XCENTER_PV_MODULATION_POWER.address, const.XCENTER_PV_MODULATION_POWER.scale, signed=False, unit="W")
    target_temperature_heating = gauge(
        const.XCENTER_PV_TARGET_TEMPERATURE_HEATING.address,
        const.XCENTER_PV_TARGET_TEMPERATURE_HEATING.scale,
        signed=True,
        unit="°C",
        writable=True,
    )
    target_temperature_dhw = gauge(
        const.XCENTER_PV_TARGET_TEMPERATURE_DHW.address,
        const.XCENTER_PV_TARGET_TEMPERATURE_DHW.scale,
        signed=True,
        unit="°C",
        writable=True,
    )
