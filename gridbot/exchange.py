"""Börsen-Anbindung: Paper (Simulation) und Live (ccxt)."""
from __future__ import annotations

import itertools
from dataclasses import dataclass


@dataclass
class Order:
    id: str
    side: str
    price: float
    amount: float
    filled: bool = False


class PaperExchange:
    """Simuliert Limit-Orders gegen einen Preis-Feed."""

    def __init__(self, price_fn, fee_pct: float = 0.1):
        self._price_fn = price_fn
        self.fee_pct = fee_pct
        self.orders: dict[str, Order] = {}
        self._ids = itertools.count(1)

    def price(self, symbol: str) -> float:
        return self._price_fn(symbol)

    def check_market(self, symbol: str, quote_per_grid: float, levels: list[float]) -> None:
        pass

    def market_buy(self, symbol: str, amount: float) -> float:
        return self.price(symbol)

    def limit_order(self, symbol: str, side: str, price: float, amount: float) -> str:
        oid = f"p{next(self._ids)}"
        self.orders[oid] = Order(oid, side, price, amount)
        return oid

    def is_filled(self, symbol: str, oid: str) -> bool:
        o = self.orders[oid]
        if not o.filled:
            p = self.price(symbol)
            o.filled = p <= o.price if o.side == "buy" else p >= o.price
        return o.filled

    def cancel_all(self, symbol: str) -> None:
        self.orders = {k: o for k, o in self.orders.items() if o.filled}


class LiveExchange:
    """Echte Orders über ccxt (z. B. crypto.com)."""

    def __init__(self, exchange_id: str, api_key: str, secret: str):
        import ccxt

        self.ex = getattr(ccxt, exchange_id)({"apiKey": api_key, "secret": secret, "enableRateLimit": True})
        self.ex.load_markets()

    def price(self, symbol: str) -> float:
        return float(self.ex.fetch_ticker(symbol)["last"])

    def check_market(self, symbol: str, quote_per_grid: float, levels: list[float]) -> None:
        """Bricht ab, wenn das Paar fehlt oder die Order-Größe unter dem Börsen-Minimum liegt."""
        m = self.ex.markets.get(symbol)
        if not m or not m.get("active", True):
            raise RuntimeError(f"{symbol} ist auf {self.ex.id} nicht handelbar")
        min_cost = (m["limits"]["cost"] or {}).get("min") or 0
        min_amt = (m["limits"]["amount"] or {}).get("min") or 0
        if quote_per_grid < min_cost:
            raise RuntimeError(f"{symbol}: {quote_per_grid:.2f} je Grid < Mindestwert {min_cost} – weniger Grids/mehr Investment")
        if quote_per_grid / levels[-1] < min_amt:
            raise RuntimeError(f"{symbol}: Ordermenge unter Mindestmenge {min_amt}")

    def market_buy(self, symbol: str, amount: float) -> float:
        o = self.ex.create_market_buy_order(symbol, self.ex.amount_to_precision(symbol, amount))
        return float(o.get("average") or self.price(symbol))

    def limit_order(self, symbol: str, side: str, price: float, amount: float) -> str:
        o = self.ex.create_limit_order(
            symbol, side, float(self.ex.amount_to_precision(symbol, amount)),
            float(self.ex.price_to_precision(symbol, price)),
            {"postOnly": True},  # garantiert Maker-Gebühr (0 %); wird abgelehnt statt als Taker gefüllt
        )
        return o["id"]

    def is_filled(self, symbol: str, oid: str) -> bool:
        return self.ex.fetch_order(oid, symbol)["status"] == "closed"

    def cancel_all(self, symbol: str) -> None:
        self.ex.cancel_all_orders(symbol)
