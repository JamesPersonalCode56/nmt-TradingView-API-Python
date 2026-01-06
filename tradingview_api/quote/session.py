from ..utils import gen_session_id
from .market import quote_market_constructor


def _get_quote_fields(fields_type):
    if fields_type == "price":
        return ["lp"]
    return [
        "base-currency-logoid",
        "ch",
        "chp",
        "currency-logoid",
        "currency_code",
        "current_session",
        "description",
        "exchange",
        "format",
        "fractional",
        "is_tradable",
        "language",
        "local_description",
        "logoid",
        "lp",
        "lp_time",
        "minmov",
        "minmove2",
        "original_name",
        "pricescale",
        "pro_name",
        "short_name",
        "type",
        "update_mode",
        "volume",
        "ask",
        "bid",
        "fundamentals",
        "high_price",
        "low_price",
        "open_price",
        "prev_close_price",
        "rch",
        "rchp",
        "rtc",
        "rtc_time",
        "status",
        "industry",
        "basic_eps_net_income",
        "beta_1_year",
        "market_cap_basic",
        "earnings_per_share_basic_ttm",
        "price_earnings_ttm",
        "sector",
        "dividends_yield",
        "timezone",
        "country_code",
        "provider_id",
    ]


def quote_session_generator(client):
    class QuoteSession:
        def __init__(self, options=None):
            options = options or {}
            self._session_id = gen_session_id("qs")
            self._client = client
            self._symbol_listeners = {}

            client["sessions"][self._session_id] = {
                "type": "quote",
                "onData": self._on_data,
            }

            fields = (
                options.get("customFields")
                if options.get("customFields")
                else _get_quote_fields(options.get("fields"))
            )

            client["send"]("quote_create_session", [self._session_id])
            client["send"]("quote_set_fields", [self._session_id, *fields])

            self._quote_session = {
                "sessionID": self._session_id,
                "symbolListeners": self._symbol_listeners,
                "send": client["send"],
                "debug": client.get("debug"),
            }

            self.Market = quote_market_constructor(self._quote_session)

        def _on_data(self, packet):
            if self._client.get("debug"):
                print("QUOTE SESSION DATA", packet)

            packet_type = packet.get("type")
            data = packet.get("data", [])
            if packet_type == "quote_completed":
                symbol_key = data[1]
                if symbol_key not in self._symbol_listeners:
                    self._client["send"]("quote_remove_symbols", [self._session_id, symbol_key])
                    return
                for handler in self._symbol_listeners[symbol_key]:
                    if handler:
                        handler(packet)

            if packet_type == "qsd":
                symbol_key = data[1].get("n") if len(data) > 1 and isinstance(data[1], dict) else None
                if not symbol_key:
                    return
                if symbol_key not in self._symbol_listeners:
                    self._client["send"]("quote_remove_symbols", [self._session_id, symbol_key])
                    return
                for handler in self._symbol_listeners.get(symbol_key, []):
                    if handler:
                        handler(packet)

        def delete(self):
            self._client["send"]("quote_delete_session", [self._session_id])
            self._client["sessions"].pop(self._session_id, None)

    return QuoteSession
