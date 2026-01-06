import pytest

import tradingview_api as TradingView
from .utils import calculate_time_gap, wait, wait_for


@pytest.mark.network
def test_simple_chart_session():
    client = TradingView.Client()
    chart = client.Session.Chart()

    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "D"})

    assert wait_for(
        lambda: chart.infos.get("full_name") == "BINANCE:BTCEUR" and len(chart.periods) >= 10,
        timeout=20,
    )

    assert chart.infos.get("full_name") == "BINANCE:BTCEUR"
    assert calculate_time_gap(chart.periods) == 24 * 60 * 60

    wait(1000)
    chart.setSeries("15")

    assert wait_for(lambda: len(chart.periods) >= 10, timeout=20)
    assert calculate_time_gap(chart.periods) == 15 * 60

    wait(1000)
    chart.setMarket("BINANCE:ETHEUR", {"timeframe": "D", "type": "HeikinAshi"})

    assert wait_for(lambda: chart.infos.get("full_name") == "BINANCE:ETHEUR", timeout=20)

    chart.delete()
    client.end()
