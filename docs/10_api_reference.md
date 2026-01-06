# 10 - API Reference

All names follow the JS library style (camelCase).

## Module functions (tradingview_api)

- `getTA(market_id)`
  - market_id: "EXCHANGE:SYMBOL" (example: "BINANCE:BTCUSDT")
  - return: dict of periods -> {Other, All, MA}

- `searchMarket(search, filter="")`
  - search: string keywords
  - filter: optional market type
  - return: list of dicts with keys `id`, `symbol`, `exchange`, `description`, `getTA`

- `searchMarketV3(search, filter="", offset=0)`
  - newer search endpoint

- `searchIndicator(search="")`
  - return: list of dicts with keys `id`, `name`, `author`, `type`, `get`

- `getIndicator(indicator_id, version="last", session="", signature="")`
  - indicator_id example: "STD;Supertrend%Strategy" or "PUB;xxxxx"
  - return: `PineIndicator`
  - note: private indicators require session/signature

- `loginUser(username, password, remember=True, UA="TWAPI/3.0")`
  - return: user dict containing `session` and `signature`

- `getUser(session, signature="", location="https://www.tradingview.com/")`
  - return: user dict

- `getPrivateIndicators(session, signature="")`
  - return: list of private indicator entries, each has a `get()` function

- `getChartToken(layout, credentials=None)`
  - credentials: {id, session, signature}
  - return: token string

- `getDrawings(layout, symbol="", credentials=None, chart_id="_shared")`
  - return: list of drawings

## Client

Create:

```python
client = TradingView.Client(options)
```

Options:

- `token`: sessionid cookie
- `signature`: sessionid_sign cookie
- `server`: "data" | "prodata" | "widgetdata"
- `location`: TradingView base URL
- `DEBUG`: enable debug logging

Properties:

- `isLogged`
- `isOpen`

Methods:

- `send(type, params=[])`
- `sendQueue()`
- `onConnected(cb)`
- `onDisconnected(cb)`
- `onLogged(cb)`
- `onPing(cb)`
- `onData(cb)`
- `onError(cb)`
- `onEvent(cb)`
- `end()`

## Chart session

Create:

```python
chart = client.Session.Chart()
```

Properties:

- `infos`: symbol metadata
- `periods`: list of candles (latest first)
- `Study`: constructor for studies

Methods:

- `setMarket(symbol, options={})`
  - options: timeframe, range, to, adjustment, backadjustment, session, currency, type, inputs, replay

- `setSeries(timeframe="240", range=100, reference=None)`
- `setTimezone(timezone)`
- `fetchMore(number=1)`
- `replayStep(number=1)` -> Future
- `replayStart(interval=1000)` -> Future
- `replayStop()` -> Future
- `delete()`

Events:

- `onSymbolLoaded(cb)`
- `onUpdate(cb)`
- `onReplayLoaded(cb)`
- `onReplayPoint(cb)`
- `onReplayResolution(cb)`
- `onReplayEnd(cb)`
- `onError(cb)`
- `onEvent(cb)`

## Chart Study

Create:

```python
study = chart.Study(indicator)
```

Properties:

- `instance`: indicator instance
- `periods`: list of plot values
- `graphic`: parsed graphic data
- `strategyReport`: strategy performance report

Methods:

- `setIndicator(indicator)`
- `onReady(cb)`
- `onUpdate(cb)`
- `onError(cb)`
- `onEvent(cb)`
- `remove()`

## Quote session

Create:

```python
quote = client.Session.Quote({"fields": "all"})
market = quote.Market("BTCEUR")
```

Quote options:

- `fields`: "all" | "price"
- `customFields`: list of field names

Market methods:

- `onLoaded(cb)`
- `onData(cb)`
- `onError(cb)`
- `onEvent(cb)`
- `close()`

Quote session methods:

- `delete()`

## PineIndicator

Create with `getIndicator()`. Methods:

- `setOption(key, value)`
- `setType(type)`

Properties:

- `pineId`, `pineVersion`
- `description`, `shortDescription`
- `inputs`, `plots`, `script`
- `type`

## BuiltInIndicator

Create:

```python
indicator = TradingView.BuiltInIndicator("VbPFixed@tv-basicstudies-241!")
```

Methods:

- `setOption(key, value, FORCE=False)`

Properties:

- `type`
- `options`

## PinePermManager

Create:

```python
manager = TradingView.PinePermManager(session, signature, pine_id)
```

Methods:

- `getUsers(limit=10, order="-created")`
- `addUser(username, expiration=None)`
- `modifyExpiration(username, expiration=None)`
- `removeUser(username)`

