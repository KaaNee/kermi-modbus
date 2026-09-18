# kermi-modbus

Asynchrones Python-Package zum Lesen und Schreiben von Kermi-Wärmepumpen (x-center /
x-change dynamic pro) über Modbus TCP.

Die Bibliothek ist backend-neutral: sie konsumiert eine
[`modbus_connection.ModbusUnit`](https://home-assistant-libs.github.io/modbus-connection/)
und öffnet die Verbindung nicht selbst. Anwendungen können daher `tmodbus`, `pymodbus` oder
ein anderes von `modbus-connection` unterstütztes Backend verwenden.

Architektur und Vorgehen orientieren sich an
[`trovis-modbus`](https://github.com/Tom-Bom-badil/trovis-modbus) (vom Home-Assistant-Team
selbst als Vorbild empfohlen) und direkt an
[`e3dc-modbus`](https://github.com/KaaNee/e3dc-modbus) (gleicher Autor, gleiche
Ziel-Library, bereits gegen echte Hardware verifiziert). Lebt seit 2026-09-18 ebenfalls als
eigenes Repo: [github.com/KaaNee/kermi-modbus](https://github.com/KaaNee/kermi-modbus)
(Split aus dem `ha-kermi`-Monorepo, analog `e3dc-modbus`).

> [!NOTE]
> Noch NICHT gegen echte Hardware verifiziert. Registeradressen und Skalierungen kommen aus
> Kermis eigener Modbus-Registerliste (`2023-10-11_Modbusliste_dynamic pro_mod1.xlsx`),
> abgeglichen mit einer echten, produktiven Home-Assistant-`modbus.yaml` (siehe
> `../kermi-modbus-projektplan.md`). Das deckt alle Lesewerte ab, die in Produktion bereits
> funktionieren. Die Schreibregister (Sollwerte, Betriebsarten, Einmalladung) und ein Teil der
> reinen Lesewerte (z. B. die Betriebsstunden-Skalierung, siehe `const.py`) sind bisher nur
> dokumentiert, nicht real getestet.

## Zwei Modbus-Units, nicht eine

Anders als bei E3DC (eine Unit) besteht eine Kermi-Installation aus zwei Geräten auf
demselben Modbus-TCP-Endpunkt, unterschieden nur über die Unit-/Slave-ID:

| Gerät | Unit-ID | Python-Typ |
|---|---|---|
| x-center / x-change dynamic pro | 40 (Kaskade: 41, 42, ...) | `KermiXCenter` |
| Speichersystemmodul | 50 und/oder 51 | `KermiStorageModule` |

`KermiDevice` bündelt eine x-center-Unit mit null oder mehreren Speichersystemmodul-Units.
Ob 50 und 51 zwei physisch getrennte Module sind oder ein Modul, das auf beiden IDs identisch
antwortet, ist noch nicht geklärt (siehe Projektplan §10.1). Die Bibliothek unterstützt beide
Fälle, indem sie das volle dokumentierte Registerset auf jede übergebene Unit anwendet.

## Unterstützte Modelle

| Modell | Status |
|---|---|
| Kermi x-change dynamic pro | einziges dokumentiertes/abgeglichenes Profil |
| Bösch (österreichische Sub-Marke) | laut Referenz-openHAB-Binding "nearly identical", nicht verifiziert |

Anders als bei E3DC gibt es kein bekanntes Identifikations-Register (Hersteller/Modell/
Seriennummer) irgendwo in Kermis Registerliste. `KermiDevice` kann das Modell daher nicht per
`async_probe()` erkennen (siehe `models/_base.py`). Der Aufrufer gibt das Profil explizit an
(Default: das eine verifizierte Profil, x-change dynamic pro).

## Umfang / bewusste Auslassungen

- PV-Modulation (Adressen 300-303): standardmäßig deaktiviert (`include_pv_modulation`
  Parameter). Das Referenz-openHAB-Binding macht dasselbe (`pvEnabled`, Default `false`), das
  x-center reagiert nachweislich empfindlich auf zu aggressives Polling.
- Kaskade (Unit 41/42): in der Registerliste dokumentiert, aber nicht implementiert, niemand
  an diesem Projekt hat eine Kaskaden-Installation zum Testen.
- Keine Energie-/Kosten-Sensoren: Kermi dokumentiert nirgends Lifetime-Energiezähler, nur
  Momentanleistung (kW) und Betriebsstunden. Energiebilanz ist bewusst nicht Teil dieser
  Library (siehe Projektplan §8).

## Basic usage

```python
import asyncio

from modbus_connection.tmodbus import connect_tcp
from kermi_modbus import KermiDevice

async def main() -> None:
    # Kermi spricht natives Modbus TCP (MBAP-Framing), daher framer="socket".
    connection = await connect_tcp("192.168.1.50", port=502, framer="socket")
    try:
        xcenter_unit = connection.for_unit(40)
        storage_unit = connection.for_unit(50)

        device = KermiDevice(xcenter_unit, (storage_unit,))
        await device.async_update()

        print("Status:", device.xcenter.state.global_state.name)
        print("COP:", device.xcenter.power.cop)
        print("Vorlauftemperatur:", device.xcenter.charging_circuit.flow_temperature, "°C")
    finally:
        await connection.close()

asyncio.run(main())
```

## Entwicklung

```bash
python -m pip install -e ".[dev]"
pytest
```

Der Testsuite-Ansatz folgt `e3dc-modbus`/`trovis-modbus`: Tests laufen gegen das
In-Memory-Mock-Backend von `modbus-connection` (`modbus_connection.mock.MockModbusConnection`),
keine echte Hardware nötig.

## CLI-Tool

```bash
python -m pip install -e ".[cli]"
python script/query.py 192.168.1.50 --xcenter-unit 40 --storage-unit 50 --storage-unit 51
```

## Lizenz

Apache-2.0, siehe `LICENSE`.
