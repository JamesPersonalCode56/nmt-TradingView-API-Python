# TradingView API (Python)

Python port of the TradingView API wrapper.

## Quick start

Install in a local environment:

```bash
pip install -e .
```

Create a client and read chart data:

```python
import tradingview_api as TradingView

client = TradingView.Client()
chart = client.Session.Chart()

chart.setMarket("BINANCE:BTCEUR", {"timeframe": "D"})

def on_loaded():
    print("Loaded", chart.infos.get("full_name"))

chart.onSymbolLoaded(on_loaded)
```

More details:

- `docs/` for full documentation and API reference.
- `examples/` for runnable samples (some require `SESSION`/`SIGNATURE`).
