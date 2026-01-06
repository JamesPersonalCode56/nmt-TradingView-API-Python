import tradingview_api as TradingView

results = TradingView.searchMarketV3("BINANCE:BTCUSDT")
print("Markets:", len(results))

indicators = TradingView.searchIndicator("RSI")
print("Indicators:", len(indicators))
