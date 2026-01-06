# 01 - Overview

This package is a Python port of the TradingView API wrapper.
It exposes the same API surface as the original JS library:

- Client: WebSocket connection manager
- Sessions: Chart and Quote
- Indicators: PineIndicator and BuiltInIndicator
- Utility HTTP requests: search, technical analysis, login, drawings

The library is event-driven: data arrives asynchronously over WebSocket and
callbacks are used to react to updates.

Key design points:

- One Client holds a single WebSocket connection.
- You can create multiple Chart or Quote sessions from one Client.
- Indicators are attached to a Chart session as Study objects.
- Many features require an authenticated TradingView session.

Quick map:

- `tradingview_api.Client`: core entry point
- `Client.Session.Chart`: chart data, replay, studies
- `Client.Session.Quote`: quote data for symbols
- `tradingview_api.getIndicator`: fetch Pine script definitions
- `tradingview_api.searchMarketV3` / `searchIndicator`: search utilities

