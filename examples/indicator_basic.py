import os

import tradingview_api as TradingView

indicator = TradingView.getIndicator("STD;Supertrend%Strategy")
print("Indicator:", indicator.description)

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if session and signature:
    client = TradingView.Client({"token": session, "signature": signature})
    chart = client.Session.Chart()
    chart.setMarket("BINANCE:BTCEUR", {"timeframe": "60"})

    def on_loaded():
        study = chart.Study(indicator)
        print("Study created", study)

    chart.onSymbolLoaded(on_loaded)
else:
    print("Set SESSION and SIGNATURE to use chart + private indicators.")
