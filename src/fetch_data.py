import csv
import time
from datetime import datetime, timezone

import tradingview_api as TradingView

# Nếu cần auth thì bật dòng dưới:
# client = TradingView.Client({"token": session, "signature": signature})
client = TradingView.Client()
chart = client.Session.Chart()

chart.onError(lambda *err: print("Chart error:", *err))

target_total = 1000
batch = 200

chart.setMarket("BINANCE:BTCUSDT.P", {"timeframe": "15", "range": batch})

def wait_for_count(n, timeout=30):
    start = time.time()
    while len(chart.periods) < n and time.time() - start < timeout:
        time.sleep(0.2)

# Đợt 1
wait_for_count(batch)

# 4 đợt tiếp theo
for i in range(1, target_total // batch):
    chart.fetchMore(batch)
    wait_for_count(batch * (i + 1))

# Gộp + loại trùng theo time
by_time = {p["time"]: p for p in chart.periods}
rows = sorted(by_time.values(), key=lambda p: p["time"])

with open("candles_15m.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["datetime", "open", "high", "low", "close", "volume"])
    for p in rows[:target_total]:
        dt = datetime.fromtimestamp(p["time"], tz=timezone.utc).isoformat()
        writer.writerow([dt, p["open"], p["max"], p["min"], p["close"], p["volume"]])

chart.delete()
client.end()
