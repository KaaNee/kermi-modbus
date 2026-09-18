"""Enum types for Kermi's status/mode registers.

Values come from the manufacturer Excel (see const.py / project plan §5).
None of these registers are configured with an ``nan`` sentinel anywhere in
this library — see const.py's module docstring for why: the real production
YAML did that with ``nan_value``, which hid the valid "0" state as
`unknown` in Home Assistant. Do not add ``nan=`` to any of the ``enum()``
fields built from these types without concrete evidence of a real sentinel.
"""

from __future__ import annotations

from enum import IntEnum


class GlobalState(IntEnum):
    """x-center address 200 — "Status Gesamtanlage"."""

    STANDBY = 0
    ALARM = 1
    DHW = 2
    COOLING = 3
    HEATING = 4
    DEFROST = 5
    PREPARING = 6
    BLOCKED = 7
    EVU_BLOCKTIME = 8
    UNAVAILABLE = 9


class HeatingCircuitStatus(IntEnum):
    """Storage module address 150 — "Status Heizkreis"."""

    OFF = 0
    HEATING = 1
    COOLING = 2
    DEW_POINT = 3
    PUMP_MAINTENANCE_RUN = 4
    FROST_PROTECTION = 5
    MANUAL_OPERATION = 6
    TEST_MODE = 7
    INITIALIZING = 8
    SAFETY_STATE = 9


class OperatingMode(IntEnum):
    """Storage module address 153 — "Betriebsmodus" (read-only status)."""

    OFF = 0
    HEATING = 1
    COOLING = 2


class OperatingType(IntEnum):
    """Storage module address 154 — "Betriebsart" (writable)."""

    AUTO = 0
    OFF = 1


class EnergyMode(IntEnum):
    """Storage module address 155 — "Energiemodus" (writable)."""

    OFF = 0
    ECO = 1
    NORMAL = 2
    COMFORT = 3
    CUSTOM = 4


class SeasonSelection(IntEnum):
    """Storage module address 157 — "Manuelle Saisonauswahl" (writable)."""

    AUTO = 0
    HEATING = 1
    COOLING = 2
    OFF = 3


class ExternalHeatGeneratorMode(IntEnum):
    """Storage module addresses 201/203 — "Betriebsart Heizen/TWE" (writable).

    Write path CONFIRMED against real hardware (2026-09-14, script/query.py
    --test-ext-heat-generator-mode-write): AUTO -> HEAT_PUMP_ONLY -> AUTO
    round-tripped and read back correctly on both unit 50 (register 201) and
    unit 51 (register 203) — the last of the 15 documented writable
    registers, and the highest-impact pair (project plan §12).
    """

    AUTO = 0
    HEAT_PUMP_ONLY = 1
    BOTH = 2
    SECONDARY_HEAT_GENERATOR_ONLY = 3


class ExternalHeatGeneratorStatus(IntEnum):
    """Storage module addresses 200/202 — "Status ext. WEZ Heizen/TWE".

    Sparse: only these specific values are documented (0, 100, 200-209,
    300-309) — not a dense 0..309 range. A raw value outside this set means
    either an undocumented state or a misread register; do not assume it
    silently rounds to something nearby.
    """

    NO_REQUEST = 0
    REQUEST = 100

    READY_AUTO_PARALLEL = 200
    READY_AUTO_ALTERNATIVE = 201
    READY_AUTO_PARTIAL_PARALLEL_PARALLEL = 202
    READY_AUTO_PARTIAL_PARALLEL_ALTERNATIVE = 203
    READY_DUE_TO_FAULT = 204
    READY_MANUAL_PARALLEL = 205
    READY_DUE_TO_MANUAL_PARALLEL = 206
    READY_EVU_BLOCKTIME = 207
    READY_EXTERNAL_REQUEST = 208
    READY_EXTERNAL_REQUEST_COMFORT = 209

    REQUEST_AUTO_PARALLEL = 300
    REQUEST_AUTO_ALTERNATIVE = 301
    REQUEST_AUTO_PARTIAL_PARALLEL_PARALLEL = 302
    REQUEST_AUTO_PARTIAL_PARALLEL_ALTERNATIVE = 303
    REQUEST_DUE_TO_FAULT = 304
    REQUEST_MANUAL_PARALLEL = 305
    REQUEST_DUE_TO_MANUAL_PARALLEL = 306
    REQUEST_EVU_BLOCKTIME = 307
    REQUEST_EXTERNAL_REQUEST = 308
    REQUEST_EXTERNAL_REQUEST_COMFORT = 309
