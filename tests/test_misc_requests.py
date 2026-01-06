import os

import pytest

import tradingview_api as TradingView


def _skip_network():
    return os.getenv("TRADINGVIEW_SKIP_NETWORK") == "1"


@pytest.mark.network
@pytest.mark.skipif(_skip_network(), reason="Network tests disabled")
def test_search_market_v3():
    results = TradingView.searchMarketV3("BINANCE:BTCUSDT")
    if not results:
        pytest.skip("No market results")
    first = results[0]
    assert "id" in first
    assert "getTA" in first


@pytest.mark.network
@pytest.mark.skipif(_skip_network(), reason="Network tests disabled")
def test_search_indicator():
    results = TradingView.searchIndicator("RSI")
    assert isinstance(results, list)
    if not results:
        pytest.skip("No indicator results")
    assert "id" in results[0]


@pytest.mark.network
@pytest.mark.skipif(_skip_network(), reason="Network tests disabled")
def test_get_ta_from_search_result():
    results = TradingView.searchMarketV3("BINANCE:BTCUSDT")
    if not results:
        pytest.skip("No market results")
    ta = results[0]["getTA"]()
    assert ta
    for period in ["1", "5", "15", "60", "240", "1D", "1W", "1M"]:
        assert period in ta
        assert "Other" in ta[period]
        assert "All" in ta[period]
        assert "MA" in ta[period]
