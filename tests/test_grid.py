import pytest

from gridbot.bot import GridBot
from gridbot.exchange import PaperExchange
from gridbot.grid import make_levels, net_step_pct

CFG = {"symbol": "X/USDT", "lower": 90, "upper": 110, "grids": 4, "investment": 400, "mode": "arithmetic"}


def test_levels():
    lv = make_levels(90, 110, 4, "arithmetic")
    assert lv == [90, 95, 100, 105, 110]
    g = make_levels(4.5, 6.2, 14)
    assert g[0] == pytest.approx(4.5) and g[-1] == pytest.approx(6.2)


def test_fee_guard():
    assert net_step_pct(make_levels(90, 110, 4), 0.1) > 0
    with pytest.raises(ValueError):
        GridBot("T", {**CFG, "grids": 200, "lower": 99, "upper": 101}, None)


def test_cycle_makes_profit(tmp_path):
    price = {"p": 100.5}
    ex = PaperExchange(lambda s: price["p"])
    bot = GridBot("T", CFG, ex, str(tmp_path))
    bot.start()
    for p in (94.9, 100.5, 105.1, 99.9, 105.1):  # Kauf @95, Verkauf @100, Kauf @95, Verkauf @100 ...
        price["p"] = p
        bot.step()
    assert bot.cycles >= 1 and bot.profit > 0


def test_stop_loss(tmp_path):
    price = {"p": 100.0}
    bot = GridBot("T", {**CFG, "stop_loss": 85}, PaperExchange(lambda s: price["p"]), str(tmp_path))
    bot.start()
    price["p"] = 84
    bot.step()
    assert bot.stopped and not bot.open
