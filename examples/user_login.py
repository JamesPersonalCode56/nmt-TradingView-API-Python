import sys

import tradingview_api as TradingView

if len(sys.argv) < 3:
    raise RuntimeError("Please specify username/email and password")

username = sys.argv[1]
password = sys.argv[2]

try:
    user = TradingView.loginUser(username, password, False)
    print("User:", user)
    print("Session:", user.get("session"))
    print("Signature:", user.get("signature"))
except Exception as exc:
    print("Login error:", exc)
