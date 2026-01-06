import os
import pytest


def pytest_collection_modifyitems(config, items):
    skip_network = os.getenv("TRADINGVIEW_SKIP_NETWORK") == "1"
    if not skip_network:
        return

    skip_marker = pytest.mark.skip(reason="Network tests disabled")
    for item in items:
        if "network" in item.keywords:
            item.add_marker(skip_marker)
