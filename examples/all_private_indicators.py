import os
import tradingview_api as TradingView

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

client = TradingView.Client({"token": session, "signature": signature})
chart = client.Session.Chart()
chart.setMarket("BINANCE:BTCEUR", {"timeframe": "D"})

indicators = TradingView.getPrivateIndicators(session, signature)
if not indicators:
    raise RuntimeError("No private indicators")

for indic in indicators:
    private_indic = indic["get"]()
    print("Loading indicator", indic["name"], "...")

    study = chart.Study(private_indic)

    study.onReady(lambda name=indic["name"]: print("Indicator", name, "loaded!"))

    def on_update(_changes=None, name=indic["name"], st=study):
        if st.periods:
            print("Plot values", st.periods[0])
        if st.strategyReport:
            print("Strategy report", st.strategyReport)

    study.onUpdate(on_update)
