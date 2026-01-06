import os
import threading

import pytest

import tradingview_api as TradingView


@pytest.mark.network
def test_get_indicator_public():
    indicator = TradingView.getIndicator("STD;Supertrend%Strategy")
    assert indicator is not None
    assert indicator.description == "Supertrend Strategy"

    indicator.setOption("commission_type", "percent")
    indicator.setOption("commission_value", 0)
    indicator.setOption("initial_capital", 25000)
    indicator.setOption("default_qty_value", 20)
    indicator.setOption("default_qty_type", "percent_of_equity")
    indicator.setOption("currency", "EUR")
    indicator.setOption("pyramiding", 10)

    other = TradingView.getIndicator("PUB;uA35GeckoTA2EfgI63SD2WCSmca4njxp")
    assert other.description == "VuManChu B Divergences"

    other.setOption("Show_WT_Hidden_Divergences", True)
    other.setOption("Show_Stoch_Regular_Divergences", True)
    other.setOption("Show_Stoch_Hidden_Divergences", True)


@pytest.mark.network
@pytest.mark.skipif(
    not os.getenv("SESSION") or not os.getenv("SIGNATURE"),
    reason="Missing SESSION/SIGNATURE",
)
def test_indicator_on_chart():
    token = os.getenv("SESSION")
    signature = os.getenv("SIGNATURE")

    indicator = TradingView.getIndicator("STD;Supertrend%Strategy")
    client = TradingView.Client({"token": token, "signature": signature})
    chart = client.Session.Chart()

    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "60"})

    loaded = threading.Event()
    updated = threading.Event()

    chart.onSymbolLoaded(lambda: loaded.set())

    assert loaded.wait(20)

    study = chart.Study(indicator)

    def on_update(_changes=None):
        if study.strategyReport.get("performance"):
            updated.set()

    study.onUpdate(on_update)

    assert updated.wait(20)

    chart.delete()
    client.end()
