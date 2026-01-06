import os

import tradingview_api as TradingView

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

client = TradingView.Client({"token": session, "signature": signature})
chart = client.Session.Chart()

chart.setTimezone("Europe/Paris")
chart.setMarket("CAPITALCOM:US100", {"timeframe": "1S", "range": 10})

chart.onSymbolLoaded(lambda: print(chart.infos.get("name"), "loaded!"))


def on_update(_changes=None):
    print("OK", chart.periods)
    client.end()


chart.onUpdate(on_update)
