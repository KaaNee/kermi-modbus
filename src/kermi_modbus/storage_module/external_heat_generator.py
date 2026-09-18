"""Externer Wärmeerzeuger block (project plan §5.2, addresses 200-203).

Split by domain (project plan §10.1: unit 50 = Heizkreis, unit 51 = TWE):
addresses 200/201 coordinate an external heat generator for heating, 202/203
for DHW — two independent register pairs, not one combined block.
"""

from __future__ import annotations

from modbus_connection.model import Component, enum

from .. import const
from ..enums import ExternalHeatGeneratorMode, ExternalHeatGeneratorStatus


class ExternalHeatGeneratorHeating(Component):
    """External heat-generator coordination for the heating circuit (unit 50).

    Call ``async_update()`` to refresh.
    """

    status = enum(
        const.STORAGE_EXT_HEAT_GENERATOR_HEATING_STATUS.address,
        ExternalHeatGeneratorStatus,
        signed=False,
    )
    mode = enum(
        const.STORAGE_EXT_HEAT_GENERATOR_HEATING_MODE.address,
        ExternalHeatGeneratorMode,
        signed=False,
        writable=True,
    )


class ExternalHeatGeneratorDhw(Component):
    """External heat-generator coordination for DHW (unit 51).

    Call ``async_update()`` to refresh.
    """

    status = enum(
        const.STORAGE_EXT_HEAT_GENERATOR_DHW_STATUS.address,
        ExternalHeatGeneratorStatus,
        signed=False,
    )
    mode = enum(
        const.STORAGE_EXT_HEAT_GENERATOR_DHW_MODE.address,
        ExternalHeatGeneratorMode,
        signed=False,
        writable=True,
    )
