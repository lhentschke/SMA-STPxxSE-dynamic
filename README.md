# Grid-Bots auf crypto.com Exchange (manuell per GUI)

Exchange → *Trading Bots* → *Grid Trading* (Manual Mode). Gebühren: Maker 0 % / Taker 0,088 %.
Gridtyp **Geometric**, **Trailing Up aus**, Stop-Loss immer setzen.

Kurse (Stand 01.10.2026): CRO 0,06853 · NEAR 4,9448 · BONK 0,000003728 · ADA 0,24552 · XRP 1,4795

## Parameter

| | CRO/USD | NEAR/USD | BONK/USD | ADA/USDT | XRP/USDT |
|---|---|---|---|---|---|
| Investment | **2.000 USD** | 900 USD | 250 USD | 400 USDT | 300 USDT |
| Untergrenze | 0,054 (−21,2 %) | 3,80 (−23,2 %) | 0,0000030 (−19,5 %) | 0,205 (−16,5 %) | 1,25 (−15,5 %) |
| Obergrenze | 0,078 (+13,8 %) | 5,60 (+13,3 %) | 0,0000046 (+23,4 %) | 0,285 (+16,1 %) | 1,70 (+14,9 %) |
| Bandbreite | 44,4 % | 47,4 % | 53,3 % | 39,0 % | 36,0 % |
| Grids | 12 | 12 | 8 | 24 | 10 |
| Abstand je Grid | ca. 3,1 % | ca. 3,3 % | ca. 5,5 % | ca. 1,4 % | ca. 3,1 % |
| Order je Grid | ca. 167 USD | 75 USD | ca. 31 USD | ca. 17 USDT | 30 USDT |
| Stop-Loss | 0,050 (−27,0 %) | 3,50 (−29,2 %) | 0,0000027 (−27,6 %) | 0,19 (−22,6 %) | 1,15 (−22,3 %) |

Prozentwerte = Abstand zum Kurs oben. Bandbreite = Obergrenze ÷ Untergrenze − 1.
ADA/XRP funktionieren bei Bedarf auch als /USD-Paar mit denselben Werten.

## Kapital
Bots: 3.150 USD + 700 USDT = 3.850 (ca. 72 % von ca. 5.340). Reserve: ca. 1.250 USD + 240 USDT zum Nachkaufen bei Rücksetzern.

## Reihenfolge (Termine laut Nachrichtenlage vom 01.10.2026, nicht geprüft)
1. **ADA** sofort (ruhigster Coin) – **läuft seit 01.10.2026** (400 USDT, 24 Grids).
2. **CRO** nach den Abstimmungen am **3.10.** (228 Mio. CRO Burn, Revenue-Backed CRO); Upgrade v1.8 am 22.10.
3. **NEAR** nach dem **5.10.** (Upgrade, Gas-Rückerstattung entfällt; ETF-Zuflüsse); +180 % im September, überhitzt.
4. **XRP** nach dem **9.10.** (Protokoll-Updates 5./9.10., Evernorth/Nasdaq 7./8.10., Swell 27.–29.10.).
5. **BONK** zuletzt und klein, nach dem **7.10.** (Upbit-Delisting, Abhebungen bis dahin offen).

## Risiken
- Fällt der Kurs unter die Untergrenze, bleibst du auf dem Bestand sitzen; über der Obergrenze ist alles verkauft.
- Vor jedem Start Kurs gegen das Raster prüfen (Kurs muss innerhalb liegen).
- Keine Anlageberatung.
