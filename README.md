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
[`e3dc-modbus`](https://github.com/KaaNee/e3dc-modbus) (gleicher Autor, gleiche Ziel-Library,
bereits gegen echte Hardware verifiziert).

> [!NOTE]
> Registeradressen und Skalierungen kommen aus Kermis eigener Modbus-Registerliste,
> abgeglichen mit einer echten, produktiven Home-Assistant-`modbus.yaml`. Gegen echte
> Hardware bestätigt: die Betriebsstunden-Skalierung des x-center, der Modulaufteilung
> zwischen Heizkreis- und TWE-Speichermodul, sowie die Schreibpfade für PV-Modulation und für
> den externen Wärmeerzeuger. Die übrigen Register, darunter die meisten Lesewerte, sind
> dokumentiert und gegen die produktive YAML abgeglichen, aber noch nicht einzeln gegen echte
> Hardware verifiziert.

## Zwei Modbus-Units, nicht eine

Anders als bei E3DC (eine Unit) besteht eine Kermi-Installation aus zwei Geräten auf
demselben Modbus-TCP-Endpunkt, unterschieden nur über die Unit-/Slave-ID:

| Gerät | Unit-ID | Python-Typ |
|---|---|---|
| x-center / x-change dynamic pro | 40 (Kaskade: 41, 42, ...) | `KermiXCenter` |
| Heizkreis-Speichermodul | 50 (optional) | `KermiHeatingCircuitModule` |
| TWE-Speichermodul | 51 (optional) | `KermiDhwModule` |

`KermiDevice` bündelt eine x-center-Unit mit null, einer oder beiden Speichermodul-Units.
Heizkreis- und TWE-Modul sind zwei physisch getrennte Module, die je nur ihre eigenen
Register beantworten (bestätigt gegen echte Hardware); eine Installation kann eines, beide
oder keines davon haben.

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
- Kaskade (Unit 41/42): in der Registerliste dokumentiert, aber nicht implementiert, kein
  Testgerät verfügbar.
- Keine Energie-/Kosten-Sensoren: Kermi dokumentiert nirgends Lifetime-Energiezähler, nur
  Momentanleistung (kW) und Betriebsstunden. Energiebilanz ist bewusst nicht Teil dieser
  Library.

## Basic usage

```python
import asyncio

from modbus_connection.tmodbus import connect_tcp
from kermi_modbus import KermiDevice

async def main() -> None:
    # Kermi spricht natives Modbus TCP (MBAP-Framing).
    connection = await connect_tcp("192.168.1.50", port=502)
    try:
        xcenter_unit = connection.for_unit(40)
        heating_circuit_unit = connection.for_unit(50)
        dhw_unit = connection.for_unit(51)

        device = KermiDevice(
            xcenter_unit,
            heating_circuit_unit=heating_circuit_unit,
            dhw_unit=dhw_unit,
        )
        await device.async_update()

        print("Status:", device.xcenter.state.global_state.name)
        print("COP:", device.xcenter.power.cop)
        print("Vorlauftemperatur:", device.xcenter.charging_circuit.flow_temperature, "°C")
        print("TWE-Temperatur:", device.dhw_module.dhw.actual_temperature, "°C")
    finally:
        await connection.close()

asyncio.run(main())
```

Heizkreis- und TWE-Unit sind optional: `KermiDevice(xcenter_unit)` reicht, wenn nur das
x-center angebunden werden soll.

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
python script/query.py 192.168.1.50 --xcenter-unit 40 --heating-circuit-unit 50 --dhw-unit 51
```

## Lizenz

Apache-2.0, siehe `LICENSE`.
