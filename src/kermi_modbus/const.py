"""Register metadata for the Kermi Modbus device library.

Primary source: Kermi's own "2023-10-11_Modbusliste_dynamic pro_mod1.xlsx"
(register list for the x-change dynamic pro / x-center, dated 2023-10-11).
Cross-checked against a real, working Home Assistant `modbus.yaml` for a
Kermi x-change dynamic pro (see ../kermi-modbus-projektplan.md, Abschnitt 5).

Two Modbus units, not one:
  - x-center / x-change dynamic pro — unit ID 40 (cascade slaves: 41, 42, ...)
  - Speichersystemmodul (storage module) — unit ID 50 and/or 51

No register offset: unlike some other manufacturers' Modbus docs, Kermi's
documented "Datenpunkt Adresse" IS the wire register address directly (no
+/-1 correction). Verified against the real production YAML (address 100 on
unit 51 reads the DHW actual temperature correctly with no offset applied).

IMPORTANT — the "FLOAT" type column in the manufacturer Excel is misleading:
every register in this file — including ones Kermi's own sheet types as
"FLOAT" — is a single INT16 register with a 0.1 scale factor, not a FLOAT32
spanning two registers. This was verified empirically against the real
production YAML (e.g. address 100 on unit 51 with scale 0.1 correctly
yields 48.5 °C) and the source Excel has since been corrected in place
(FLOAT -> INT16, factor 0.1 added) — see kermi-modbus-projektplan.md,
Abschnitt 10.

IMPORTANT — no NaN sentinel values are configured on enum/status registers
in this library, and none should be added without real evidence. The real
production `modbus.yaml` set `nan_value: 0` (and similar) on several status
registers, which silently turned the valid "0" state ("Standby", "Aus",
"keine Anforderung", ...) into `unknown` in Home Assistant — a production
bug, not a device quirk. See kermi-modbus-projektplan.md, Abschnitt 4.

Deliberately NOT modeled here (see project plan): no model/manufacturer/
serial-number identification registers are documented anywhere in the Kermi
register list (unlike E3DC's rich info block) — there is currently no known
way to probe which Kermi model is connected. Model selection in this library
is therefore caller-provided, not detected. See models/_base.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RegisterKind(str, Enum):
    """Which Modbus table a register lives in. Kermi documents everything as
    a plain "Register" (holding register, function code 03/06/16) — no coils,
    no input registers are used anywhere in the manufacturer's register list.
    """

    HOLDING = "holding"


@dataclass(frozen=True)
class Register:
    """Metadata describing a single Modbus datapoint.

    ``address`` is the wire address (no offset, see module docstring).

    ``min_value``/``max_value``/``default`` are DOCUMENTATION ONLY — plain
    data carried over from the manufacturer Excel. Nothing in this file
    applies them automatically; a subsystem module (see xcenter/,
    storage_module/) must explicitly wire a writable register's range into
    a real write-time check via ``validation.range_validator(register)``.
    They must NEVER be used to clamp or filter a *read* value — that is
    exactly the real production bug documented above (nan_value / clamping
    min_value/max_value on enum registers silently hid the valid "0"
    state). Read-side filtering and write-side validation are deliberately
    different code paths in this library.
    """

    address: int
    kind: RegisterKind = RegisterKind.HOLDING
    scale: float = 1.0
    signed: bool = False
    unit: str | None = None
    device_class: str | None = None
    state_class: str | None = None
    writable: bool = False
    min_value: float | None = None
    max_value: float | None = None
    default: float | None = None


# =============================================================================
# x-center / x-change dynamic pro — unit ID 40 (cascade: 41, 42, ...)
# =============================================================================

# --- Energiequelle (project plan §5.1, addresses 1-3) -----------------------
XCENTER_EXIT_TEMPERATURE = Register(1, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
XCENTER_INCOMING_TEMPERATURE = Register(2, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
XCENTER_OUTSIDE_TEMPERATURE = Register(3, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")

# --- Ladekreis (project plan §5.1, addresses 50-52) -------------------------
XCENTER_FLOW_TEMPERATURE = Register(50, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
XCENTER_RETURN_TEMPERATURE = Register(51, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
XCENTER_FLOW_SPEED = Register(52, scale=0.1, unit="l/min", state_class="measurement")

# --- Leistung und Effizienz (project plan §5.1, addresses 100-111) ---------
# COP values are unsigned in practice (a heat pump's COP is never negative);
# the Excel documents plain "INT16" without specifying sign.
XCENTER_COP = Register(100, scale=0.1, state_class="measurement")
XCENTER_COP_HEATING = Register(101, scale=0.1, state_class="measurement")
XCENTER_COP_DHW = Register(102, scale=0.1, state_class="measurement")
XCENTER_COP_COOLING = Register(103, scale=0.1, state_class="measurement")

XCENTER_POWER = Register(104, scale=0.1, unit="kW", device_class="power", state_class="measurement")
XCENTER_POWER_HEATING = Register(105, scale=0.1, unit="kW", device_class="power", state_class="measurement")
XCENTER_POWER_DHW = Register(106, scale=0.1, unit="kW", device_class="power", state_class="measurement")
XCENTER_POWER_COOLING = Register(107, scale=0.1, unit="kW", device_class="power", state_class="measurement")

# The real production YAML omitted the scale factor on 108 entirely (own
# comment: "value is kW * 10") — that was a config bug, not a register
# property. The Excel documents the same 0.1 factor as 104-107/109-111 for
# all four electric-power registers; use it uniformly.
XCENTER_ELECTRIC_POWER = Register(108, scale=0.1, unit="kW", device_class="power", state_class="measurement")
XCENTER_ELECTRIC_POWER_HEATING = Register(109, scale=0.1, unit="kW", device_class="power", state_class="measurement")
XCENTER_ELECTRIC_POWER_DHW = Register(110, scale=0.1, unit="kW", device_class="power", state_class="measurement")
XCENTER_ELECTRIC_POWER_COOLING = Register(111, scale=0.1, unit="kW", device_class="power", state_class="measurement")

# --- Betriebsstunden (project plan §5.1, addresses 150-152) -----------------
# Factor 0.1 CONFIRMED against real hardware (2026-09-11, script/query.py):
# register 152 raw = 59232 -> 5923.2 h; register 150 (fan) independently
# decodes to 5892.9 h — fan and compressor runtime being nearly identical is
# exactly what's physically expected (the fan runs whenever the compressor
# does), corroborating the factor rather than merely trusting the Excel.
# The 0.1-scale uint16 ceiling (6553.5 h) is a real long-term register-design
# limitation — it will eventually wrap on a long-lived, heavily-used unit —
# but that was never evidence against the *current* factor, only against
# extrapolating it indefinitely into the future.
XCENTER_WORKHOURS_FAN = Register(150, scale=0.1, unit="h", state_class="measurement")
XCENTER_WORKHOURS_STORAGE_LOADING_PUMP = Register(151, scale=0.1, unit="h", state_class="measurement")
XCENTER_WORKHOURS_COMPRESSOR = Register(152, scale=0.1, unit="h", state_class="measurement")

# --- Status (project plan §5.1, address 200) --------------------------------
# Plain uint16, values 0-9 (GlobalState enum, see enums.py). NOT bit-packed —
# openHAB's StateDTO reads this with extractBit(), which can only ever
# return 0 or 1; that is a bug in the reference binding, not a register
# property (see project plan §6.1). No `nan` value configured here — 0
# ("Standby") is a valid, common state (see module docstring).
#
# max_value=10 is the Excel's OWN off-by-one: it lists exactly 10 named
# values (0-9) but documents "Max: 10" — copied here verbatim since this
# field is documentation-only (see the Register docstring above), not
# enforced. modbus_connection's enum() field does not raise on an
# undocumented raw value; it decodes it as None and logs a warning
# (verified empirically) — callers reading global_state must handle None,
# not assume every read returns a GlobalState member. This matters far
# more for the sparse ExternalHeatGeneratorStatus enum below, where large
# gaps between documented values are the norm, not the exception.
XCENTER_GLOBAL_STATE = Register(200, min_value=0, max_value=10)

# --- Statusmeldungen (project plan §5.1, address 250) -----------------------
XCENTER_ALARM_ACTIVE = Register(250, min_value=0, max_value=1)

# --- PV Modulation Wärmepumpe (project plan §5.1, addresses 300-303) --------
XCENTER_PV_MODULATION_ACTIVE = Register(300, min_value=0, max_value=1)
# Excel documents 0.1 W here — the openHAB binding's PvDTO used the same 0.1
# factor while its PowerDTO used 100 for physically the same kind of
# quantity (a factor-1000 mismatch between two binding classes for the same
# device — see project plan §6.1). Trust the Excel's per-register factor,
# not the binding's cross-class consistency.
XCENTER_PV_MODULATION_POWER = Register(301, scale=0.1, unit="W", device_class="power", state_class="measurement")
XCENTER_PV_TARGET_TEMPERATURE_HEATING = Register(
    302, scale=0.1, unit="°C", device_class="temperature", writable=True, default=50
)
XCENTER_PV_TARGET_TEMPERATURE_DHW = Register(
    303, scale=0.1, unit="°C", device_class="temperature", writable=True, default=50
)


# =============================================================================
# Speichersystemmodul (storage module) — unit ID 50 and/or 51
#
# The real production YAML reads DHW registers (100-104) from unit 51 and
# heating-circuit/status registers (150-156, 254-255) from unit 50 —
# concurrently, not as alternatives.
#
# CONFIRMED against real hardware (project plan §10.1, 2026-09-11): 50 and 51
# are functionally SEPARATE modules (50 = heating circuit, 51 = DHW), not the
# same module answering twice. A read on the "wrong" unit doesn't raise a
# Modbus error, it silently returns 0 / a default value. This file still
# documents the FULL register set Kermi's Excel assigns to "Device 50/51" as
# one model, but device.py now wires each register group to only ONE of
# KermiHeatingCircuitModule (unit 50) or KermiDhwModule (unit 51) — the
# domain split is implemented, not merely documented here.
# =============================================================================

# --- Heizen: Pufferspeicher (project plan §5.2, addresses 1-2) --------------
STORAGE_BUFFER_ACTUAL_TEMPERATURE = Register(1, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_BUFFER_TARGET_TEMPERATURE = Register(2, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")

# --- Kühlen: Kühlpufferspeicher (project plan §5.2, addresses 50-51) -------
STORAGE_COOLING_BUFFER_ACTUAL_TEMPERATURE = Register(50, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_COOLING_BUFFER_TARGET_TEMPERATURE = Register(51, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")

# --- Trinkwassererwärmung / DHW (project plan §5.2, addresses 100-104) -----
STORAGE_DHW_ACTUAL_TEMPERATURE = Register(100, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_DHW_TARGET_TEMPERATURE = Register(101, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_DHW_CONSTANT_SETPOINT = Register(
    102, scale=0.1, unit="°C", device_class="temperature", writable=True,
    min_value=0, max_value=85, default=48,
)
# Full register 0/1, not bit-packed (same caveat as XCENTER_GLOBAL_STATE).
# The real production YAML had `max_value: 4` on this register — inconsistent
# with the Excel's own BOOL/0-1 typing for it (looks like a copy-paste from
# the neighbouring energy-mode register) and has been corrected here.
STORAGE_DHW_SINGLE_CHARGE = Register(103, writable=True, min_value=0, max_value=1, default=0)
STORAGE_DHW_SINGLE_CHARGE_SETPOINT = Register(
    104, scale=0.1, unit="°C", device_class="temperature", writable=True,
    min_value=30, max_value=60, default=50,
)

# --- Heizkreis (project plan §5.2, addresses 150-163) -----------------------
# Enum, 0-9 (HeatingCircuitStatus, see enums.py).
STORAGE_HEATING_CIRCUIT_STATUS = Register(150, min_value=0, max_value=9)
STORAGE_HEATING_CIRCUIT_ACTUAL_TEMPERATURE = Register(151, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
# Read-only (Excel: "R") despite carrying a documented Min/Max range — do
# NOT expose this as a writable `number`; the actual setpoint is derived
# from 154-157, not written here directly.
STORAGE_HEATING_CIRCUIT_TARGET_TEMPERATURE = Register(
    152, scale=0.1, unit="°C", device_class="temperature", state_class="measurement",
    min_value=0, max_value=85,
)
# Enum, 0-2 (OperatingMode, see enums.py). Read-only status; the writable
# counterpart is OPERATING_TYPE (154) below.
STORAGE_OPERATING_MODE = Register(153, min_value=0, max_value=2)
# Enum, 0-1 (OperatingType, see enums.py).
STORAGE_OPERATING_TYPE = Register(154, writable=True, min_value=0, max_value=1, default=0)
# Enum, 0-4 (EnergyMode, see enums.py).
STORAGE_ENERGY_MODE = Register(155, writable=True, min_value=0, max_value=4, default=2)
# Signed! -5..5. This is the one field where the openHAB binding's use of an
# unsigned read (PowerDTO.getUDoubleValue) would silently misdecode negative
# values (see project plan §6.1) — must be read/written as signed.
STORAGE_HEATING_CURVE_PARALLEL_SHIFT = Register(
    156, signed=True, writable=True, min_value=-5, max_value=5, default=0,
    state_class="measurement",
)
# Enum, 0-3 (SeasonSelection, see enums.py).
STORAGE_MANUAL_SEASON_SELECTION = Register(157, writable=True, min_value=0, max_value=3, default=0)
STORAGE_SUMMER_MODE_OFF_THRESHOLD = Register(
    158, scale=0.1, unit="°C", device_class="temperature", writable=True,
    min_value=0, max_value=50, default=18,
)
STORAGE_WINTER_MODE_ON_THRESHOLD = Register(
    159, scale=0.1, unit="°C", device_class="temperature", writable=True,
    min_value=0, max_value=50, default=16,
)
STORAGE_COOLING_MODE_ON_THRESHOLD = Register(
    160, scale=0.1, unit="°C", device_class="temperature", writable=True,
    min_value=0, max_value=50, default=22,
)
STORAGE_COOLING_MODE_OFF_THRESHOLD = Register(
    161, scale=0.1, unit="°C", device_class="temperature", writable=True,
    min_value=0, max_value=50, default=20,
)
STORAGE_SUMMER_MODE_ACTIVE = Register(162, min_value=0, max_value=1)
STORAGE_COOLING_MODE_ACTIVE = Register(163, min_value=0, max_value=1)

# --- Externer Wärmeerzeuger (project plan §5.2, addresses 200-203) ---------
# Sparse enum: 0, 100, 200-209, 300-309 (ExternalHeatGeneratorStatus).
STORAGE_EXT_HEAT_GENERATOR_HEATING_STATUS = Register(200, min_value=0, max_value=309)
# Enum, 0-3 (ExternalHeatGeneratorMode, see enums.py).
STORAGE_EXT_HEAT_GENERATOR_HEATING_MODE = Register(201, writable=True, min_value=0, max_value=3, default=0)
STORAGE_EXT_HEAT_GENERATOR_DHW_STATUS = Register(202, min_value=0, max_value=309)
STORAGE_EXT_HEAT_GENERATOR_DHW_MODE = Register(203, writable=True, min_value=0, max_value=3, default=0)

# --- Status: freie Fühler + Außentemperatur (project plan §5.2, 250-255) ---
STORAGE_SENSOR_1 = Register(250, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_SENSOR_2 = Register(251, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_SENSOR_3 = Register(252, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_SENSOR_4 = Register(253, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_OUTSIDE_TEMPERATURE = Register(254, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")
STORAGE_OUTSIDE_TEMPERATURE_AVERAGED = Register(255, scale=0.1, unit="°C", device_class="temperature", state_class="measurement")

# --- Betriebsstunden (project plan §5.2, addresses 300-301) -----------------
# Excel documents Min 0 / Max 65535 / Default 0 with NO scale factor for
# these two (unlike the x-center's 150-152, which document 0.1) — raw hours.
STORAGE_HEATING_CIRCUIT_PUMP_WORKHOURS = Register(300, unit="h", min_value=0, max_value=65535, state_class="measurement")
STORAGE_HEATING_ROD_WORKHOURS = Register(301, unit="h", min_value=0, max_value=65535, state_class="measurement")
