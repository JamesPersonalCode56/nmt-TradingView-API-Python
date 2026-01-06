import os
import threading
import time

import tradingview_api as TradingView

client = TradingView.Client(
    {
        "token": os.getenv("SESSION"),
        "signature": os.getenv("SIGNATURE"),
    }
)

chart = client.Session.Chart()


def on_error(*err):
    print("Chart error:", *err)


def on_update(_changes=None):
    if chart.periods:
        print("Last period", chart.periods[0])


chart.onError(on_error)
chart.onUpdate(on_update)


def set_chart(chart_type, symbol, inputs=None):
    options = {"type": chart_type, "timeframe": "D"}
    if inputs:
        options["inputs"] = inputs
    chart.setMarket(symbol, options)


def close_client():
    print("\nClosing client...")
    client.end()


threading.Timer(0, lambda: (print("\nSetting chart type to: HeikinAshi"), set_chart("HeikinAshi", "BINANCE:BTCEUR"))).start()
threading.Timer(5, lambda: (print("\nSetting chart type to: Renko"), set_chart("Renko", "BINANCE:BTCEUR", {
    "source": "close",
    "sources": "Close",
    "boxSize": 3,
    "style": "ATR",
    "atrLength": 14,
    "wicks": True,
}))).start()
threading.Timer(10, lambda: (print("\nSetting chart type to: LineBreak"), set_chart("LineBreak", "BINANCE:BTCEUR", {"source": "close", "lb": 3}))).start()
threading.Timer(15, lambda: (print("\nSetting chart type to: Kagi"), set_chart("Kagi", "BINANCE:BTCEUR", {"source": "close", "style": "ATR", "atrLength": 14, "reversalAmount": 1}))).start()
threading.Timer(20, lambda: (print("\nSetting chart type to: PointAndFigure"), set_chart("PointAndFigure", "BINANCE:BTCEUR", {
    "sources": "Close",
    "reversalAmount": 3,
    "boxSize": 1,
    "style": "ATR",
    "atrLength": 14,
    "oneStepBackBuilding": False,
}))).start()
threading.Timer(25, lambda: (print("\nSetting chart type to: Range"), set_chart("Range", "BINANCE:BTCEUR", {"range": 1, "phantomBars": False}))).start()
threading.Timer(30, close_client).start()

while client.isOpen:
    time.sleep(0.5)
