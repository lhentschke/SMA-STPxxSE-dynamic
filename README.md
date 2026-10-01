# Grid-Bot für crypto.com Exchange (NEAR, BONK)

Parameter in `config.yaml` stammen aus der Bewertung vom 01.10.2026:

| | NEAR | BONK |
|---|---|---|
| Rolle | Hauptposition (700 USDT) | Spekulation (150 USDT) |
| Raster | 4,50–6,20 USDT, 14 Grids | 0,0000030–0,0000046 USDT, 8 Grids |
| Stop-Loss | 4,20 | 0,0000027 |
| Begründung | Rally +175 %/30 Tage: Raster um Unterstützung 5,00 / Widerstand 5,50, Rücksetzer werden eingesammelt | hohes Totalverlust-Risiko: klein halten, weit, enger Stop |

**Vor dem Start prüfen:** Preise stammen aus Websuchen und sind evtl. veraltet. `lower`/`upper` an den aktuellen Kurs anpassen.
Der Bot bricht ab, wenn der Kurs außerhalb des Rasters liegt, die Gebühren den Grid-Abstand auffressen
oder crypto.com das Paar bzw. die Mindestordergröße nicht zulässt.

## Start
```
pip install -r requirements.txt
python -m gridbot            # mode: paper (Simulation, nur öffentliche Preise)
```
Live: `mode: live` setzen, API-Key in crypto.com Exchange anlegen (nur *Trade*, **kein Withdraw**, IP-Whitelist):
```
export EXCHANGE_API_KEY=... EXCHANGE_SECRET=...
python -m gridbot
```
Mind. eine Woche im Paper-Modus laufen lassen, bevor du live gehst.

## Home Assistant
Mit `HA_URL` (z. B. `http://homeassistant.local:8123`) und `HA_TOKEN` (Long-Lived Access Token) legt der Bot
`sensor.gridbot_near` / `sensor.gridbot_bonk` an (Zustand = Gewinn in USDT; Attribute: Kurs, Zyklen, offene Orders, gestoppt).
Betrieb z. B. als Add-on, systemd-Dienst oder Docker-Container.

## Risiken
- Grid-Bots verlieren bei Trends aus dem Raster (Bestand wird zum Bag). Der Stop-Loss storniert nur Orders, er verkauft den Bestand nicht.
- Zustand der offenen Orders wird nicht wiederhergestellt: nach Neustart `cancel_all` auf der Börse ausführen und neu starten.
- Keine Anlageberatung.
