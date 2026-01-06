import os
import threading

import pytest

import tradingview_api as TradingView
from .utils import wait_for


@pytest.mark.network
@pytest.mark.skipif(
    not os.getenv("SESSION") or not os.getenv("SIGNATURE"),
    reason="Missing SESSION/SIGNATURE",
)
def test_authenticated_actions():
    token = os.getenv("SESSION")
    signature = os.getenv("SIGNATURE")

    user = TradingView.getUser(token, signature)
    assert user.get("id")
    assert user.get("username")
    assert user.get("notifications")
    assert user.get("notifications").get("following") is not None
    assert user.get("notifications").get("user") is not None

    private_indicators = TradingView.getPrivateIndicators(token)
    assert isinstance(private_indicators, list)

    client = TradingView.Client({"token": token, "signature": signature})
    chart = client.Session.Chart()
    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "D"})

    assert wait_for(lambda: chart.infos.get("full_name") == "BINANCE:BTCEUR", timeout=20)

    tested = private_indicators[:3]
    if not tested:
        pytest.skip("No private indicators")

    loaded_count = 0
    loaded_event = threading.Event()

    def on_update():
        nonlocal loaded_count
        loaded_count += 1
        if loaded_count >= len(tested) + 1:
            loaded_event.set()

    chart.onUpdate(lambda _changes=None: on_update())

    for item in tested:
        indicator = item["get"]()
        study = chart.Study(indicator)
        study.onUpdate(lambda _changes=None: on_update())

    assert loaded_event.wait(30)

    chart.delete()
    client.end()
