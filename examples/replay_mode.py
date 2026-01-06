import os
import threading
import time

import tradingview_api as TradingView

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

print("----- Testing ReplayMode -----")

client = TradingView.Client({"token": session, "signature": signature})
chart = client.Session.Chart()

config = {
    "symbol": "BINANCE:BTCEUR",
    "timeframe": "D",
    "startFrom": int(time.time()) - 86400 * 7,
}

chart.setMarket(
    config["symbol"],
    {"timeframe": config["timeframe"], "replay": config["startFrom"], "range": 1},
)

interval = None
periods = {}
indicators = []
replay_end = threading.Event()


def add_indicator(name, pine_id, options=None):
    options = options or {}
    if "@" in pine_id:
        indic = TradingView.BuiltInIndicator(pine_id)
    else:
        indic = TradingView.getIndicator(pine_id)

    for key, value in options.items():
        indic.setOption(key, value)

    study = chart.Study(indic)
    study.onReady(lambda: indicators.append((name, study)))


add_indicator("Volume", "Volume@tv-basicstudies-241")
add_indicator("EMA_50", "STD;EMA", {"Length": 50})
add_indicator("EMA_200", "STD;EMA", {"Length": 200})

chart.onReplayEnd(lambda: replay_end.set())

print("Stepping replay...")
while True:
    if not chart.periods:
        time.sleep(0.2)
        continue

    period = dict(chart.periods[0])
    times = list(periods.keys())
    if len(times) >= 2:
        intrval = times[-1] - times[-2]
        if interval is None:
            interval = intrval
        elif interval != intrval:
            raise RuntimeError(f"Wrong interval: {intrval} (should be {interval})")

    for name, indicator in indicators:
        plots = dict(indicator.periods[0]) if indicator.periods else {}
        plots.pop("$time", None)
        period[name] = {"plots": plots}

        graphics = indicator.graphic
        for g_name, g_list in graphics.items():
            if not isinstance(g_list, list) or not g_list:
                continue
            period[name].setdefault("graphics", {})[g_name] = g_list

    periods[period["time"]] = period
    print("Next ->", period["time"], len(periods))

    future = chart.replayStep(1)
    future.result(timeout=10)
    time.sleep(0.2)

    if replay_end.is_set():
        break

    if len(periods) > 50:
        break

client.end()
print("Done!", len(periods))
