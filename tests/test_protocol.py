from tradingview_api.protocol import format_ws_packet, parse_ws_packet


def test_format_and_parse_roundtrip():
    payload = {"m": "test", "p": ["session", {"key": "value"}]}
    packed = format_ws_packet(payload)
    assert packed.startswith("~m~")

    parsed = parse_ws_packet(packed)
    assert parsed == [payload]


def test_parse_multiple_packets():
    packets = [
        {"m": "one", "p": [1]},
        {"m": "two", "p": [2]},
    ]
    packed = "".join(format_ws_packet(p) for p in packets)
    parsed = parse_ws_packet(packed)
    assert parsed == packets


def test_parse_invalid_json_is_ignored():
    broken = "~m~4~m~nope"
    assert parse_ws_packet(broken) == []
