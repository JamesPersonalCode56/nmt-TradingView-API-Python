import os
import threading
from concurrent.futures import ThreadPoolExecutor

import tradingview_api as TradingView

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

client = TradingView.Client({"token": session, "signature": signature})


def get_indicator_data(indicator):
    chart = client.Session.Chart()
    chart.setMarket("BINANCE:DOTUSDT")
    study = chart.Study(indicator)

    print(f"Getting '{indicator.description}'...")

    event = threading.Event()
    holder = {"periods": []}

    def on_update(_changes=None):
        holder["periods"] = study.periods
        event.set()

    study.onUpdate(on_update)
    event.wait(20)
    chart.delete()

    print(f"'{indicator.description}' done!")
    return holder["periods"]


print("Getting all indicators...")
indicators = [
    TradingView.getIndicator("PUB;3lEKXjKWycY5fFZRYYujEy8fxzRRUyF3"),
    TradingView.getIndicator("PUB;5nawr3gCESvSHQfOhrLPqQqT4zM23w3X"),
    TradingView.getIndicator("PUB;vrOJcNRPULteowIsuP6iHn3GIxBJdXwT"),
]

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(get_indicator_data, indicators))

print(results)
print("All done!")
client.end()
