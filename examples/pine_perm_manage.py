import os
import sys
from datetime import datetime, timedelta

from tradingview_api import PinePermManager

session = os.getenv("SESSION")
signature = os.getenv("SIGNATURE")

if not session or not signature:
    raise RuntimeError("Please set SESSION and SIGNATURE env vars")

if len(sys.argv) < 2:
    raise RuntimeError("Please specify a pine id as first argument")

pine_id = sys.argv[1]

print("Pine ID:", pine_id)

manager = PinePermManager(session, signature, pine_id)

print("Users:", manager.getUsers())

print("Adding user 'TradingView'...")
status = manager.addUser("TradingView")
if status == "ok":
    print("Done!")
elif status == "exists":
    print("This user is already authorized")
else:
    print("Unknown error...")

print("Users:", manager.getUsers())

print("Modifying expiration date...")
new_date = datetime.utcnow() + timedelta(days=1)
status = manager.modifyExpiration("TradingView", new_date)
print("Status:", status)

print("Users:", manager.getUsers())

print("Removing expiration date...")
status = manager.modifyExpiration("TradingView")
print("Status:", status)

print("Users:", manager.getUsers())

print("Removing user 'TradingView'...")
status = manager.removeUser("TradingView")
print("Status:", status)

print("Users:", manager.getUsers())
