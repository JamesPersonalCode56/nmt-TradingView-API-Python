# 03 - Client and Sessions

## Client

Create one Client per process. It holds the WebSocket connection.

```python
import tradingview_api as TradingView

client = TradingView.Client()
```

Optional authenticated client:

```python
client = TradingView.Client({
    "token": session_id,
    "signature": signature,
})
```

### Client events

- `onConnected(cb)`
- `onDisconnected(cb)`
- `onLogged(cb)`
- `onPing(cb)`
- `onData(cb)`
- `onError(cb)`
- `onEvent(cb)`

## Chart session

Create a chart session from the Client:

```python
chart = client.Session.Chart()
chart.setMarket("BINANCE:BTCEUR", {"timeframe": "D"})
```

### Chart events

- `onSymbolLoaded(cb)`
- `onUpdate(cb)`
- `onReplayLoaded(cb)`
- `onReplayPoint(cb)`
- `onReplayResolution(cb)`
- `onReplayEnd(cb)`
- `onError(cb)`
- `onEvent(cb)`

### Chart data

- `chart.infos`: symbol metadata
- `chart.periods`: list of candles (sorted by time desc)

### Chart controls

- `setMarket(symbol, options)`
- `setSeries(timeframe, range=100, reference=None)`
- `setTimezone(tz)`
- `fetchMore(number)`
- `delete()`

### Replay mode

```python
chart.setMarket("BINANCE:BTCEUR", {
    "timeframe": "D",
    "replay": int(time.time()) - 86400 * 7,
    "range": 1,
})

future = chart.replayStep(1)
future.result(timeout=10)
```

## Quote session

```python
quote = client.Session.Quote({"fields": "all"})
market = quote.Market("BTCEUR")
```

### Quote events

- `Market.onLoaded(cb)`
- `Market.onData(cb)`
- `Market.onError(cb)`
- `Market.onEvent(cb)`

### Quote controls

- `Market.close()`
- `Quote.delete()`

