import threading
import time

import pytest

import tradingview_api as TradingView
from .utils import calculate_time_gap, wait


@pytest.mark.network
def test_replay_mode_steps():
    client = TradingView.Client()
    chart = client.Session.Chart()

    chart.setMarket(
        "BINANCE:BTCEUR",
        {
            "timeframe": "D",
            "replay": int(time.time()) - 86400 * 10,
            "range": 1,
        },
    )

    loaded = threading.Event()
    ended = threading.Event()

    chart.onSymbolLoaded(lambda: loaded.set())
    chart.onReplayEnd(lambda: ended.set())

    assert loaded.wait(20)

    steps = 0
    while steps < 8 and not ended.is_set():
        future = chart.replayStep(1)
        future.result(timeout=10)
        wait(300)
        steps += 1

    if chart.periods:
        assert calculate_time_gap(chart.periods) == 24 * 60 * 60
        assert 2 <= len(chart.periods) <= 20

    chart.delete()
    client.end()
