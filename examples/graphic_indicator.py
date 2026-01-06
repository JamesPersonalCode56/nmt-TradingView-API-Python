import os

import tradingview_api as TradingView

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

client = TradingView.Client({"token": session, "signature": signature})
chart = client.Session.Chart()
chart.setMarket("BINANCE:BTCEUR", {"timeframe": "5", "range": 10000})

indicator = TradingView.getIndicator("STD;Zig_Zag")
study = chart.Study(indicator)


def on_error(*err):
    print("Study error:", *err)


def on_ready():
    print(f"Study '{study.instance.description}' loaded!")


def on_update(_changes=None):
    print("Graphic data:", study.graphic)
    client.end()


study.onError(on_error)
study.onReady(on_ready)
study.onUpdate(on_update)
