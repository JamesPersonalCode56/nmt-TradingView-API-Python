import threading

import pytest

import tradingview_api as TradingView

EXPECTED_KEYS = sorted(
    [
        "ask",
        "bid",
        "format",
        "volume",
        "update_mode",
        "type",
        "timezone",
        "short_name",
        "rtc_time",
        "rtc",
        "rchp",
        "ch",
        "rch",
        "provider_id",
        "pro_name",
        "pricescale",
        "prev_close_price",
        "original_name",
        "lp",
        "open_price",
        "minmove2",
        "minmov",
        "lp_time",
        "low_price",
        "is_tradable",
        "high_price",
        "fractional",
        "exchange",
        "description",
        "current_session",
        "currency_code",
        "chp",
        "currency-logoid",
        "base-currency-logoid",
    ]
)


@pytest.mark.network
def test_quote_session_fields():
    client = TradingView.Client()
    quote_session = client.Session.Quote({"fields": "all"})
    market = quote_session.Market("BTCEUR")

    loaded = threading.Event()
    data_ready = threading.Event()
    holder = {"keys": []}

    def on_loaded():
        loaded.set()

    def on_data(data):
        keys = sorted(list(data.keys()))
        if len(keys) <= 2:
            return
        holder["keys"] = keys
        data_ready.set()

    market.onLoaded(on_loaded)
    market.onData(on_data)

    assert loaded.wait(15)
    assert data_ready.wait(15)
    assert holder["keys"] == EXPECTED_KEYS

    market.close()
    quote_session.delete()
    client.end()
