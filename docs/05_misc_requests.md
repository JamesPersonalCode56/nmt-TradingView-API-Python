# 05 - Misc Requests

These helpers use HTTP endpoints (not WebSocket).

## Market search

```python
results = TradingView.searchMarketV3("BINANCE:BTCUSDT")
for item in results[:3]:
    print(item["id"], item["description"])
```

## Indicator search

```python
results = TradingView.searchIndicator("RSI")
print(len(results))
```

## Technical analysis

```python
ta = TradingView.getTA("BINANCE:BTCUSDT")
print(ta["1D"]["All"])
```

## Login and user

```python
user = TradingView.loginUser(username, password, False)
info = TradingView.getUser(user["session"], user["signature"])
```

## Private indicators

```python
priv = TradingView.getPrivateIndicators(session, signature)
for item in priv:
    indic = item["get"]()
```

## Drawings

```python
drawings = TradingView.getDrawings(layout_id, "", {
    "session": session,
    "signature": signature,
    "id": user_id,
})
```

## Pine permissions

```python
from tradingview_api import PinePermManager

manager = PinePermManager(session, signature, pine_id)
manager.getUsers()
manager.addUser("TradingView")
```

