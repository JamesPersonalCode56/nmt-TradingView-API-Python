import time

import tradingview_api as TradingView

client = TradingView.Client()
quote = client.Session.Quote({"fields": "all"})
market = quote.Market("BTCEUR")

loaded = False


def on_loaded():
    global loaded
    loaded = True
    print("Quote loaded")


def on_data(data):
    keys = list(data.keys())
    if len(keys) > 5:
        print("Last price:", data.get("lp"))


market.onLoaded(on_loaded)
market.onData(on_data)

start = time.time()
while not loaded and time.time() - start < 10:
    time.sleep(0.2)

market.close()
quote.delete()
client.end()
