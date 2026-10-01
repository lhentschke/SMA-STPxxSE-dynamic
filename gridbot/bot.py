"""Grid-Bot: Kauf unter, Verkauf über dem Kurs; jeder Fill setzt die Gegenorder."""
from __future__ import annotations

import json
import logging
import os
import time
import urllib.request
from pathlib import Path

from .grid import make_levels, net_step_pct

log = logging.getLogger("gridbot")


class GridBot:
    def __init__(self, name: str, cfg: dict, exchange, state_dir: str = "state"):
        self.name = name
        self.symbol = cfg["symbol"]
        self.ex = exchange
        self.fee = cfg.get("fee_maker_pct", 0.0)    # Grid-Orders sind Limit/Post-Only = Maker
        self.taker = cfg.get("fee_taker_pct", 0.088)  # nur Start-Marktkauf (und Notfall-Fills)
        self.lower, self.upper = cfg["lower"], cfg["upper"]
        self.stop_loss = cfg.get("stop_loss")
        self.levels = make_levels(self.lower, self.upper, cfg["grids"], cfg.get("mode", "geometric"))
        self.quote_per_grid = cfg["investment"] / cfg["grids"]
        self.open: dict[int, tuple[str, str]] = {}  # level-index -> (order_id, side)
        self.profit = 0.0
        self.cycles = 0
        self.stopped = False
        self.state_file = Path(state_dir) / f"{name}.json"

        step = net_step_pct(self.levels, self.taker)  # konservativ: Abstand muss auch Taker-Gebühren decken
        if step <= 0:
            raise ValueError(f"{name}: Grid-Abstand deckt Gebühren nicht (netto {step:.2f}%) – weniger Grids wählen")
        exchange.check_market(self.symbol, self.quote_per_grid, self.levels) if exchange else None
        log.info("%s: %d Stufen, min. Netto-Gewinn/Zyklus %.2f%%", name, len(self.levels), step)

    def start(self) -> None:
        price = self.ex.price(self.symbol)
        if not self.lower < price < self.upper:
            raise RuntimeError(f"{self.name}: Kurs {price} außerhalb {self.lower}-{self.upper}")
        sells = [i for i, lv in enumerate(self.levels) if lv > price]
        base_needed = sum(self.quote_per_grid / self.levels[i] for i in sells)
        if base_needed:
            self.ex.market_buy(self.symbol, base_needed)  # Startbestand für Verkaufsorders
            self.profit -= base_needed * price * self.taker / 100  # Taker-Gebühr des Startkaufs
        for i, lv in enumerate(self.levels):
            if lv < price:
                self._place(i, "buy")
            elif lv > price:
                self._place(i, "sell")

    def _place(self, i: int, side: str) -> None:
        price = self.levels[i]
        amount = self.quote_per_grid / price
        self.open[i] = (self.ex.limit_order(self.symbol, side, price, amount), side)

    def step(self) -> None:
        if self.stopped:
            return
        price = self.ex.price(self.symbol)
        if self.stop_loss and price <= self.stop_loss:
            log.warning("%s: Stop-Loss bei %s – Orders werden storniert", self.name, price)
            self.ex.cancel_all(self.symbol)
            self.open.clear()
            self.stopped = True
            return
        for i, (oid, side) in list(self.open.items()):
            if not self.ex.is_filled(self.symbol, oid):
                continue
            del self.open[i]
            if side == "buy" and i + 1 < len(self.levels):
                self._place(i + 1, "sell")
            elif side == "sell" and i - 1 >= 0:
                self._place(i - 1, "buy")
                gain = (self.levels[i] - self.levels[i - 1]) * self.quote_per_grid / self.levels[i - 1]
                self.profit += gain - 2 * self.fee / 100 * self.quote_per_grid
                self.cycles += 1

    def status(self) -> dict:
        return {"price": self.ex.price(self.symbol), "profit": round(self.profit, 4),
                "cycles": self.cycles, "open_orders": len(self.open), "stopped": self.stopped}

    def save(self) -> None:
        self.state_file.parent.mkdir(exist_ok=True)
        self.state_file.write_text(json.dumps(self.status()))

    def publish_ha(self) -> None:
        """Schreibt den Status als Sensor nach Home Assistant (HA_URL, HA_TOKEN)."""
        url, token = os.getenv("HA_URL"), os.getenv("HA_TOKEN")
        if not (url and token):
            return
        s = self.status()
        body = json.dumps({"state": s["profit"], "attributes": {**s, "unit_of_measurement": "USDT",
                                                                   "friendly_name": f"Gridbot {self.name}"}})
        req = urllib.request.Request(f"{url}/api/states/sensor.gridbot_{self.name.lower()}", body.encode(),
                                     {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=10)
        except OSError as e:
            log.warning("HA-Update fehlgeschlagen: %s", e)


def run(config_path: str = "config.yaml") -> None:
    import yaml

    from .exchange import LiveExchange, PaperExchange

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cfg = yaml.safe_load(Path(config_path).read_text())
    if cfg.get("mode", "paper") == "live":
        ex = LiveExchange(cfg["exchange"], os.environ["EXCHANGE_API_KEY"], os.environ["EXCHANGE_SECRET"])
    else:
        import ccxt  # öffentlicher Preis-Feed, keine Keys nötig

        feed = getattr(ccxt, cfg["exchange"])()
        ex = PaperExchange(lambda s: float(feed.fetch_ticker(s)["last"]), cfg.get("fee_taker_pct", 0.088))
        log.info("PAPER-MODUS – es werden keine echten Orders gesendet")
    bots = [GridBot(n, {**c, "fee_maker_pct": cfg.get("fee_maker_pct", 0.0), "fee_taker_pct": cfg.get("fee_taker_pct", 0.088)}, ex) for n, c in cfg["bots"].items()]
    for b in bots:
        b.start()
    while True:
        for b in bots:
            b.step()
            b.save()
            b.publish_ha()
        time.sleep(cfg.get("poll_seconds", 30))
