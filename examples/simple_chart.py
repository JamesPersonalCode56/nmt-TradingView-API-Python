import threading
import time

import tradingview_api as TradingView

client = TradingView.Client()
chart = client.Session.Chart()

chart.setMarket("BINANCE:BTCEUR", {"timeframe": "D"})


def on_error(*err):
    print("Chart error:", *err)


def on_symbol():
    print(f"Market \"{chart.infos.get('description')}\" loaded!")


def on_update(_changes=None):
    if not chart.periods:
        return
    print(f"[{chart.infos.get('description')}]: {chart.periods[0]['close']} {chart.infos.get('currency_id')}")


chart.onError(on_error)
chart.onSymbolLoaded(on_symbol)
chart.onUpdate(on_update)


def set_eth():
    print("\nSetting market to BINANCE:ETHEUR...")
    chart.setMarket("BINANCE:ETHEUR", {"timeframe": "D"})


def set_timeframe():
    print("\nSetting timeframe to 15 minutes...")
    chart.setSeries("15")


def set_heikin():
    print("\nSetting the chart type to \"Heikin Ashi\"...")
    chart.setMarket("BINANCE:ETHEUR", {"timeframe": "D", "type": "HeikinAshi"})


def close_chart():
    print("\nClosing the chart...")
    chart.delete()


def close_client():
    print("\nClosing the client...")
    client.end()


threading.Timer(5, set_eth).start()
threading.Timer(10, set_timeframe).start()
threading.Timer(15, set_heikin).start()
threading.Timer(20, close_chart).start()
threading.Timer(25, close_client).start()

time.sleep(27)
