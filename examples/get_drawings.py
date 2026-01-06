import os
import sys

import tradingview_api as TradingView

if len(sys.argv) < 2:
    raise RuntimeError("Please specify a layout ID")

layout_id = sys.argv[1]
user_id = sys.argv[2] if len(sys.argv) > 2 else None

try:
    drawings = TradingView.getDrawings(
        layout_id,
        "",
        {
            "session": os.getenv("SESSION"),
            "signature": os.getenv("SIGNATURE"),
            "id": int(user_id) if user_id else None,
        },
    )
    print(
        f"Found {len(drawings)} drawings:",
        [
            {
                "id": d.get("id"),
                "symbol": d.get("symbol"),
                "type": d.get("type"),
                "text": (d.get("state") or {}).get("text"),
            }
            for d in drawings
        ],
    )
except Exception as exc:
    print("Error:", exc)
