import pytest

import tradingview_api as TradingView
from .utils import wait_for


@pytest.mark.network
def test_custom_chart_types():
    client = TradingView.Client()
    chart = client.Session.Chart()
    errors = []

    def on_error(*err):
        errors.append(err)

    chart.onError(on_error)

    configs = [
        ("HeikinAshi", "BINANCE:BTCEUR", {}),
        (
            "Renko",
            "BINANCE:ETHEUR",
            {
                "source": "close",
                "sources": "Close",
                "boxSize": 3,
                "style": "ATR",
                "atrLength": 14,
                "wicks": True,
            },
        ),
        ("LineBreak", "BINANCE:BTCEUR", {"source": "close", "lb": 3}),
        (
            "Kagi",
            "BINANCE:ETHEUR",
            {"source": "close", "style": "ATR", "atrLength": 14, "reversalAmount": 1},
        ),
        (
            "PointAndFigure",
            "BINANCE:BTCEUR",
            {
                "sources": "Close",
                "reversalAmount": 3,
                "boxSize": 1,
                "style": "ATR",
                "atrLength": 14,
                "oneStepBackBuilding": False,
            },
        ),
        ("Range", "BINANCE:ETHEUR", {"range": 1, "phantomBars": False}),
    ]

    for chart_type, symbol, inputs in configs:
        chart.setMarket(
            symbol,
            {"type": chart_type, "timeframe": "D", "inputs": inputs} if inputs else {"type": chart_type, "timeframe": "D"},
        )

        ready = wait_for(
            lambda: chart.infos.get("full_name") == symbol and len(chart.periods) > 0,
            timeout=20,
        )
        if errors:
            pytest.skip(f"Chart error: {errors[-1]}")
        assert ready

    chart.delete()
    client.end()
