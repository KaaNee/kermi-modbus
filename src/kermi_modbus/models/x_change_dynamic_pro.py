"""Model profile for the Kermi x-change dynamic pro.

The only profile verified against the manufacturer's own register list and
a real production Home Assistant configuration (see project plan). Kermi
also sells this controller under the Austrian "Bösch" sub-brand — reported
as "nearly identical" by the reference openHAB binding's own README, but
that has not been verified here against real Bösch hardware.
"""

from __future__ import annotations

from ._base import KermiModelProfile


class XChangeDynamicProProfile(KermiModelProfile):
    name = "x-change dynamic pro"
    has_pv_modulation = True
