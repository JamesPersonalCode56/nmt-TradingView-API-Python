import threading
from types import SimpleNamespace

import websocket

from . import misc_requests
from .protocol import parse_ws_packet, format_ws_packet
from .chart.session import chart_session_generator
from .quote.session import quote_session_generator


class Client:
    def __init__(self, client_options=None):
        client_options = client_options or {}
        self._debug = bool(client_options.get("DEBUG"))
        self._logged = False
        self._connected = False
        self._sessions = {}
        self._send_queue = []
        self._callbacks = {
            "connected": [],
            "disconnected": [],
            "logged": [],
            "ping": [],
            "data": [],
            "error": [],
            "event": [],
        }

        server = client_options.get("server", "data")
        ws_url = f"wss://{server}.tradingview.com/socket.io/websocket?type=chart"

        self._ws_app = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
        )

        self._ws_thread = threading.Thread(
            target=self._ws_app.run_forever,
            kwargs={"origin": "https://www.tradingview.com"},
            daemon=True,
        )
        self._ws_thread.start()

        if client_options.get("token"):
            try:
                user = misc_requests.getUser(
                    client_options.get("token"),
                    client_options.get("signature", ""),
                    client_options.get("location", "https://tradingview.com"),
                )
                self._send_queue.insert(0, format_ws_packet({"m": "set_auth_token", "p": [user.get("authToken")]}))
                self._logged = True
                self.sendQueue()
            except Exception as exc:
                self._handle_error("Credentials error:", str(exc))
        else:
            self._send_queue.insert(0, format_ws_packet({"m": "set_auth_token", "p": ["unauthorized_user_token"]}))
            self._logged = True
            self.sendQueue()

        self._client_bridge = {
            "sessions": self._sessions,
            "send": self.send,
            "debug": self._debug,
        }

        self.Session = SimpleNamespace(
            Quote=quote_session_generator(self._client_bridge),
            Chart=chart_session_generator(self._client_bridge),
        )

    @property
    def isLogged(self):
        return self._logged

    @property
    def isOpen(self):
        return bool(self._ws_app.sock and self._ws_app.sock.connected)

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

    def _on_open(self, _ws):
        self._connected = True
        self._handle_event("connected")
        self.sendQueue()

    def _on_close(self, _ws, _status, _msg):
        self._connected = False
        self._logged = False
        self._handle_event("disconnected")

    def _on_error(self, _ws, err):
        self._handle_error("WebSocket error:", str(err))

    def _on_message(self, _ws, message):
        self._parse_packet(message)

    def _parse_packet(self, message):
        if not self.isOpen:
            return
        for packet in parse_ws_packet(message):
            if self._debug:
                print("CLIENT PACKET", packet)
            if isinstance(packet, (int, float)):
                self._ws_app.send(format_ws_packet(f"~h~{packet}"))
                self._handle_event("ping", packet)
                continue

            if isinstance(packet, dict) and packet.get("m") == "protocol_error":
                self._handle_error("Client critical error:", packet.get("p"))
                self._ws_app.close()
                return

            if isinstance(packet, dict) and packet.get("m") and packet.get("p"):
                parsed = {"type": packet.get("m"), "data": packet.get("p")}
                session = packet.get("p")[0] if packet.get("p") else None
                if session and session in self._sessions:
                    self._sessions[session]["onData"](parsed)
                    continue

            if not self._logged:
                self._handle_event("logged", packet)
                continue

            self._handle_event("data", packet)

    def send(self, packet_type, packet_data=None):
        packet_data = packet_data or []
        self._send_queue.append(format_ws_packet({"m": packet_type, "p": packet_data}))
        self.sendQueue()

    def sendQueue(self):
        while self.isOpen and self._logged and self._send_queue:
            packet = self._send_queue.pop(0)
            self._ws_app.send(packet)
            if self._debug:
                print(">", packet)

    def onConnected(self, cb):
        self._callbacks["connected"].append(cb)

    def onDisconnected(self, cb):
        self._callbacks["disconnected"].append(cb)

    def onLogged(self, cb):
        self._callbacks["logged"].append(cb)

    def onPing(self, cb):
        self._callbacks["ping"].append(cb)

    def onData(self, cb):
        self._callbacks["data"].append(cb)

    def onError(self, cb):
        self._callbacks["error"].append(cb)

    def onEvent(self, cb):
        self._callbacks["event"].append(cb)

    def end(self):
        if self._ws_app.sock:
            self._ws_app.close()
        return True
