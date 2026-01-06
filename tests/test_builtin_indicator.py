import time

import pytest

import tradingview_api as TradingView
from .utils import wait_for


@pytest.mark.network
def test_builtin_indicator_volume_profile():
    client = TradingView.Client()
    chart = client.Session.Chart()

    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "60"})
    assert wait_for(lambda: chart.infos.get("full_name") == "BINANCE:BTCEUR", timeout=20)

    volume_profile = TradingView.BuiltInIndicator("VbPFixed@tv-basicstudies-241!")
    volume_profile.setOption("first_bar_time", int(time.time() * 1000) - 10**8)

    study = chart.Study(volume_profile)

    assert wait_for(lambda: bool(study.graphic.get("horizHists")), timeout=20)

    hists = [h for h in study.graphic.get("horizHists", []) if h.get("lastBarTime") == 0]
    assert len(hists) > 5

    chart.delete()
    client.end()
