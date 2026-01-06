import csv
from datetime import datetime, timezone

import requests

SYMBOL = "BTCUSDT"
INTERVAL = "15m"
LIMIT = 1000
OUT_FILE = "candles_15m_binance.csv"

url = "https://fapi.binance.com/fapi/v1/klines"
params = {
    "symbol": SYMBOL,
    "interval": INTERVAL,
    "limit": LIMIT,
}

response = requests.get(url, params=params, timeout=15)
response.raise_for_status()

rows = response.json()

with open(OUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["datetime", "open", "high", "low", "close", "volume"])
    for row in rows:
        open_time_ms = row[0]
        dt = datetime.fromtimestamp(open_time_ms / 1000, tz=timezone.utc).isoformat()
        writer.writerow([dt, row[1], row[2], row[3], row[4], row[5]])

print(f"Saved {len(rows)} rows to {OUT_FILE}")
