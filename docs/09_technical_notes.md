# 09 - Technical Notes

## WebSocket protocol

TradingView uses a custom framing format:

- Each message is `~m~{len}~m~{json}`
- Heartbeats are prefixed with `~h~`

Parsing and formatting is in `tradingview_api/protocol.py`.

## JSON payloads

Some requests require compact JSON (no spaces). The code uses
`json.dumps(..., separators=(",", ":"))` for those payloads.

## Threading

The WebSocket client runs in a background thread.
Callbacks execute in that thread, not the main thread.
If you update UI or shared state, use thread-safe mechanisms.

## Time units

- WebSocket chart time values are seconds.
- Some endpoints use milliseconds (for example, built-in indicator options).

## Known limitations

- TradingView endpoints can change without notice.
- Replay mode and custom chart types may require auth.
- Some indicators return compressed data that must be parsed.

