import os

import tradingview_api as TradingView

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

client = TradingView.Client({"token": session, "signature": signature})
chart = client.Session.Chart()

chart.setMarket(
    "BINANCE:BTCEUR",
    {
        "timeframe": "240",
        "range": 2,
        "to": 1700000000,
    },
)

indicator = TradingView.getIndicator("STD;Supertrend")
print(f"Loading '{indicator.description}' study...")
study = chart.Study(indicator)


def on_update(_changes=None):
    print("Prices periods:", chart.periods)
    print("Study periods:", study.periods)
    client.end()


study.onUpdate(on_update)
