import os
import threading

import tradingview_api as TradingView

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

client = TradingView.Client({"token": session, "signature": signature})


def run_tests(tests):
    done = threading.Event()

    def run_next(index=0):
        if index >= len(tests):
            done.set()
            return
        tests[index](lambda: run_next(index + 1))

    run_next()
    done.wait()


def test_credentials_error(next_fn):
    print("\nTesting \"Credentials error\" error:")
    bad = TradingView.Client({"token": "FAKE_CREDENTIALS"})

    def on_error(*err):
        print(" => Client error:", err)
        bad.end()
        next_fn()

    bad.onError(on_error)


def test_invalid_symbol(next_fn):
    print("\nTesting \"Invalid symbol\" error:")
    chart = client.Session.Chart()

    def on_error(*err):
        print(" => Chart error:", err)
        chart.delete()
        next_fn()

    chart.onError(on_error)
    chart.setMarket("XXXXX")


def test_invalid_timezone(next_fn):
    print("\nTesting \"Invalid timezone\" error:")
    chart = client.Session.Chart()

    def on_error(*err):
        print(" => Chart error:", err)
        chart.delete()
        next_fn()

    chart.onError(on_error)
    chart.setMarket("BINANCE:BTCEUR")
    chart.setTimezone("Nowhere/Nowhere")


def test_custom_timeframe(next_fn):
    print("\nTesting \"Custom timeframe\" error:")
    chart = client.Session.Chart()

    def on_error(*err):
        print(" => Chart error:", err)
        chart.delete()
        next_fn()

    chart.onError(on_error)
    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "20"})


def test_invalid_timeframe(next_fn):
    print("\nTesting \"Invalid timeframe\" error:")
    chart = client.Session.Chart()

    def on_error(*err):
        print(" => Chart error:", err)
        chart.delete()
        next_fn()

    chart.onError(on_error)
    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "XX"})


def test_study_not_auth(next_fn):
    print("\nTesting \"Study not auth\" error:")
    chart = client.Session.Chart()

    def on_error(*err):
        print(" => Chart error:", err)
        chart.delete()
        next_fn()

    chart.onError(on_error)
    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "15", "type": "Renko"})


def test_set_series_before_market(next_fn):
    print("\nTesting \"Set the market before\" error:")
    chart = client.Session.Chart()

    def on_error(*err):
        print(" => Chart error:", err)
        chart.delete()
        next_fn()

    chart.onError(on_error)
    chart.setSeries("15")


def test_inexistent_indicator(next_fn):
    print("\nTesting \"Inexistent indicator\" error:")
    try:
        TradingView.getIndicator("STD;XXXXXXX")
    except Exception as exc:
        print(" => API error:", exc)
        next_fn()


def test_invalid_value(next_fn):
    print("\nTesting \"Invalid value\" error:")
    chart = client.Session.Chart()
    chart.setMarket("BINANCE:BTCEUR")

    indicator = TradingView.getIndicator("STD;Supertrend")
    indicator.setOption("Factor", -1)

    study = chart.Study(indicator)

    def on_error(*err):
        print(" => Study error:", err)
        chart.delete()
        next_fn()

    study.onError(on_error)


tests = [
    test_credentials_error,
    test_invalid_symbol,
    test_invalid_timezone,
    test_custom_timeframe,
    test_invalid_timeframe,
    test_study_not_auth,
    test_set_series_before_market,
    test_inexistent_indicator,
    test_invalid_value,
]

run_tests(tests)
client.end()
