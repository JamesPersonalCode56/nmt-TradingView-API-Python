import os
import time

import tradingview_api as TradingView

volume_profile = TradingView.BuiltInIndicator("VbPFixed@tv-basicstudies-241!")

need_auth = volume_profile.type not in {
    "VbPFixed@tv-basicstudies-241",
    "VbPFixed@tv-basicstudies-241!",
    "Volume@tv-basicstudies-241",
}

if need_auth and (not os.getenv("SESSION") or not os.getenv("SIGNATURE")):
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

client = TradingView.Client(
    {"token": os.getenv("SESSION"), "signature": os.getenv("SIGNATURE")} if need_auth else {}
)

chart = client.Session.Chart()
chart.setMarket("BINANCE:BTCEUR", {"timeframe": "60", "range": 1})

volume_profile.setOption("first_bar_time", int(time.time() * 1000) - 10**8)

study = chart.Study(volume_profile)


def on_update(_changes=None):
    hists = [
        h for h in study.graphic.get("horizHists", []) if h.get("lastBarTime") == 0
    ]
    hists.sort(key=lambda h: h.get("priceHigh", 0), reverse=True)

    for hist in hists:
        center = round((hist.get("priceHigh", 0) + hist.get("priceLow", 0)) / 2)
        print("~", center, ":", "_" * int(hist.get("rate", [0])[0] / 3))

    client.end()


study.onUpdate(on_update)
