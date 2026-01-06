import json


def quote_market_constructor(quote_session):
    class QuoteMarket:
        def __init__(self, symbol, session="regular"):
            self._symbol_listeners = quote_session["symbolListeners"]
            self._symbol = symbol
            self._session = session
            self._symbol_key = f"={json.dumps({'session': session, 'symbol': symbol}, separators=(',', ':'))}"
            self._listener_id = 0
            self._last_data = {}
            self._callbacks = {
                "loaded": [],
                "data": [],
                "event": [],
                "error": [],
            }

            if self._symbol_key not in self._symbol_listeners:
                self._symbol_listeners[self._symbol_key] = []
                quote_session["send"]("quote_add_symbols", [quote_session["sessionID"], self._symbol_key])

            self._listener_id = len(self._symbol_listeners[self._symbol_key])
            self._symbol_listeners[self._symbol_key].append(self._on_data)

        def _handle_event(self, event, *data):
            for cb in self._callbacks.get(event, []):
                cb(*data)
            for cb in self._callbacks.get("event", []):
                cb(event, *data)

        def _handle_error(self, *msgs):
            if not self._callbacks.get("error"):
                print(*msgs)
            else:
                self._handle_event("error", *msgs)

        def _on_data(self, packet):
            if quote_session.get("debug"):
                print("MARKET DATA", packet)

            if packet.get("type") == "qsd":
                payload = packet.get("data", [None, {}])[1]
                if payload.get("s") == "ok":
                    self._last_data.update(payload.get("v", {}))
                    self._handle_event("data", self._last_data)
                    return
                if payload.get("s") == "error":
                    self._handle_error("Market error", packet.get("data"))
                    return

            if packet.get("type") == "quote_completed":
                self._handle_event("loaded")

        def onLoaded(self, cb):
            self._callbacks["loaded"].append(cb)

        def onData(self, cb):
            self._callbacks["data"].append(cb)

        def onEvent(self, cb):
            self._callbacks["event"].append(cb)

        def onError(self, cb):
            self._callbacks["error"].append(cb)

        def close(self):
            listeners = self._symbol_listeners.get(self._symbol_key, [])
            if len(listeners) <= 1:
                quote_session["send"]("quote_remove_symbols", [quote_session["sessionID"], self._symbol_key])
            if self._symbol_key in self._symbol_listeners and self._listener_id < len(listeners):
                listeners[self._listener_id] = None

    return QuoteMarket
