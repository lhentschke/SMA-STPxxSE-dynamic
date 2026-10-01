"""Reine Grid-Logik (ohne Börsen-Zugriff)."""
from __future__ import annotations


def make_levels(lower: float, upper: float, grids: int, mode: str = "geometric") -> list[float]:
    """Gibt grids+1 Preisstufen zwischen lower und upper zurück."""
    if not 0 < lower < upper or grids < 2:
        raise ValueError("Ungültiger Bereich oder zu wenige Grids")
    if mode == "arithmetic":
        step = (upper - lower) / grids
        return [lower + i * step for i in range(grids + 1)]
    ratio = (upper / lower) ** (1 / grids)
    return [lower * ratio**i for i in range(grids + 1)]


def net_step_pct(levels: list[float], fee_pct: float) -> float:
    """Kleinster Netto-Gewinn je Grid-Zyklus in % (nach Gebühren für Kauf+Verkauf)."""
    gross = min(levels[i + 1] / levels[i] - 1 for i in range(len(levels) - 1)) * 100
    return gross - 2 * fee_pct
