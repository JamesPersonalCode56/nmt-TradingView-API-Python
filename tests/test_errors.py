import os
import threading

import pytest

import tradingview_api as TradingView


def wait_for_error(instance, action=None, timeout=10):
    holder = {"error": []}
    event = threading.Event()

    def on_error(*args):
        holder["error"] = list(args)
        event.set()

    instance.onError(on_error)
    if action:
        action()

    if not event.wait(timeout):
        return None
    return holder["error"]


def require_error(error):
    if error is None:
        pytest.skip("No error received from server")


@pytest.mark.network
def test_invalid_symbol_error():
    client = TradingView.Client()
    chart = client.Session.Chart()

    error = wait_for_error(chart, lambda: chart.setMarket("XXXXX"))
    require_error(error)
    assert any("Symbol error" in str(item) for item in error) or any(
        "Series error" in str(item) for item in error
    )

    chart.delete()
    client.end()


@pytest.mark.network
def test_invalid_timezone_error():
    client = TradingView.Client()
    chart = client.Session.Chart()
    chart.setMarket("BINANCE:BTCEUR")

    error = wait_for_error(chart, lambda: chart.setTimezone("Nowhere/Nowhere"))
    require_error(error)
    assert any("invalid timezone" in str(item) for item in error)

    chart.delete()
    client.end()


@pytest.mark.network
def test_invalid_timeframe_error():
    client = TradingView.Client()
    chart = client.Session.Chart()

    error = wait_for_error(chart, lambda: chart.setMarket("BINANCE:BTCEUR", {"timeframe": "XX"}))
    require_error(error)
    assert any("invalid" in str(item) for item in error)

    chart.delete()
    client.end()


@pytest.mark.network
def test_set_series_before_market_error():
    client = TradingView.Client()
    chart = client.Session.Chart()

    error = wait_for_error(chart, lambda: chart.setSeries("15"))
    require_error(error)
    assert any("set the market" in str(item) for item in error)

    chart.delete()
    client.end()


@pytest.mark.network
def test_inexistent_indicator_error():
    with pytest.raises(Exception):
        TradingView.getIndicator("STD;XXXXXXX")


@pytest.mark.network
@pytest.mark.skipif(
    not os.getenv("SESSION") or not os.getenv("SIGNATURE"),
    reason="Missing SESSION/SIGNATURE",
)
def test_invalid_study_option_error():
    token = os.getenv("SESSION")
    signature = os.getenv("SIGNATURE")

    client = TradingView.Client({"token": token, "signature": signature})
    chart = client.Session.Chart()
    chart.setMarket("BINANCE:BTCEUR")

    indicator = TradingView.getIndicator("STD;Supertrend")
    indicator.setOption("Factor", -1)

    study = chart.Study(indicator)
    error = wait_for_error(study, timeout=20)
    require_error(error)

    chart.delete()
    client.end()
