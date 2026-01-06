import time

import tradingview_api as TradingView

print("----- Testing FakeReplayMode -----")

client = TradingView.Client()
chart = client.Session.Chart()

chart.setMarket(
    "BINANCE:BTCEUR",
    {
        "timeframe": "240",
        "range": -1,
        "to": int(time.time()) - 86400 * 7,
    },
)

interval = None


def on_update(_changes=None):
    global interval
    times = [p["time"] for p in chart.periods]
    if len(times) < 2:
        return

    intrval = times[0] - times[1]
    if interval is None:
        interval = intrval
    elif interval != intrval:
        raise RuntimeError(f"Wrong interval: {intrval} (should be {interval})")

    print("Next ->", times[0])

    if times[0] > (time.time() - 86400):
        client.end()
        print("Done!", len(times))
        return

    chart.fetchMore(-2)


chart.onUpdate(on_update)

while client.isOpen:
    time.sleep(0.5)
