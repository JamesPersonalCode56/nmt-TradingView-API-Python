# 07 - Testing

Tests are located in `tests/`.

Run all tests:

```bash
pytest
```

Skip network tests:

```bash
TRADINGVIEW_SKIP_NETWORK=1 pytest
```

Notes:

- Many tests require TradingView endpoints and can be flaky.
- Authenticated tests require `SESSION` and `SIGNATURE`.
- If you see intermittent failures, retry the test or increase timeouts.

