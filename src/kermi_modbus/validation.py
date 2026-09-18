"""Write validators derived from documented register ranges.

Kermi's own register list documents Min/Max for several writable registers
(see const.py). ``modbus_connection``'s ``writable`` parameter accepts a
validator callable — a plain function that receives the value about to be
written and either returns it (or a coerced version) or raises to reject it
(see ``modbus_connection.model``'s write path, ``field.writable(value)``).
This module turns const.py's Min/Max metadata into such validators, so a
bad write (e.g. 500 degrees to a register documented as 0-85) is rejected
in Python before it reaches the device, instead of being silently accepted
and sent as-is.

These are NOT the same as the min_value/max_value clamping behaviour found
in the real production modbus.yaml (see const.py's module docstring) — that
clamped *reads* of enum/status registers, silently hiding out-of-range
values. These validators reject *writes* outside a documented range; they
never touch reads, and they are only applied to genuinely numeric
registers below, never to enum-typed ones (whose Python type already
constrains valid values).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .const import Register


class KermiValueError(ValueError):
    """Raised when a value is rejected before being written to a register."""


def range_validator(register: Register) -> Callable[[Any], Any]:
    """Build a write validator enforcing ``register``'s documented Min/Max.

    Returns the value unchanged when it is within range (or when the
    register documents no range at all); raises ``KermiValueError``
    otherwise.
    """

    def validate(value: Any) -> Any:
        number = float(value)
        if register.min_value is not None and number < register.min_value:
            raise KermiValueError(
                f"{number} is below the documented minimum {register.min_value}"
            )
        if register.max_value is not None and number > register.max_value:
            raise KermiValueError(
                f"{number} is above the documented maximum {register.max_value}"
            )
        return value

    return validate
