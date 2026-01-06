# 08 - Troubleshooting

## Common errors

### "Credentials error: Wrong or expired sessionid/signature"
- Your SESSION/SIGNATURE are invalid or expired.
- Re-login on TradingView and update env vars.

### "Critical error: invalid parameters"
- Usually caused by invalid timeframe or missing range.
- Use valid timeframes: "1", "5", "15", "60", "240", "D", "W", "M".

### "Series error: custom_resolution"
- Custom timeframes require a paid TradingView plan.

### No data / empty periods
- Wait longer: WebSocket is async.
- Check network access (firewalls or blocked endpoints).
- For intraday data, you may need auth.

## Stability tips

- Reuse a single Client instance per process.
- Avoid creating too many chart sessions at once.
- If a study or chart fails, delete it and retry.

