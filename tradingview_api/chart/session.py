import json
from concurrent.futures import Future

from ..utils import gen_session_id
from .study import study_constructor

CHART_TYPES = {
    "HeikinAshi": "BarSetHeikenAshi@tv-basicstudies-60!",
    "Renko": "BarSetRenko@tv-prostudies-40!",
    "LineBreak": "BarSetPriceBreak@tv-prostudies-34!",
    "Kagi": "BarSetKagi@tv-prostudies-34!",
    "PointAndFigure": "BarSetPnF@tv-prostudies-34!",
    "Range": "BarSetRange@tv-basicstudies-72!",
}


def chart_session_generator(client):
    class ChartSession:
        def __init__(self):
            self._chart_session_id = gen_session_id("cs")
            self._replay_session_id = gen_session_id("rs")
            self._replay_mode = False
            self._replay_ok_cb = {}
            self._client = client
            self._study_listeners = {}
            self._periods = {}
            self._infos = {}
            self._callbacks = {
                "seriesLoaded": [],
                "symbolLoaded": [],
                "update": [],
                "replayLoaded": [],
                "replayPoint": [],
                "replayResolution": [],
                "replayEnd": [],
                "event": [],
                "error": [],
            }
            self._series_created = False
            self._current_series = 0

            client["sessions"][self._chart_session_id] = {
                "type": "chart",
                "onData": self._on_chart_data,
            }

            client["sessions"][self._replay_session_id] = {
                "type": "replay",
                "onData": self._on_replay_data,
            }

            self._chart_session = {
                "sessionID": self._chart_session_id,
                "studyListeners": self._study_listeners,
                "indexes": {},
                "send": client["send"],
                "debug": client.get("debug"),
            }

            self.Study = study_constructor(self._chart_session)
            client["send"]("chart_create_session", [self._chart_session_id])

        @property
        def periods(self):
            return sorted(self._periods.values(), key=lambda p: p["time"], reverse=True)

        @property
        def infos(self):
            return self._infos

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

        def _on_chart_data(self, packet):
            if client.get("debug"):
                print("CHART SESSION DATA", packet)

            data = packet.get("data", [])
            if isinstance(data[1] if len(data) > 1 else None, str):
                listener = self._study_listeners.get(data[1])
                if listener:
                    listener(packet)
                    return

            if packet.get("type") == "symbol_resolved":
                self._infos = {"series_id": data[1], **data[2]}
                self._handle_event("symbolLoaded")
                return

            if packet.get("type") in ("timescale_update", "du"):
                changes = []
                updated = data[1] if len(data) > 1 and isinstance(data[1], dict) else {}
                for key in updated:
                    changes.append(key)
                    if key == "$prices":
                        periods = updated.get("$prices")
                        if not periods or not periods.get("s"):
                            continue
                        for entry in periods.get("s", []):
                            values = entry.get("v", [])
                            if not values:
                                continue
                            self._chart_session["indexes"][entry.get("i")] = values[0]
                            self._periods[values[0]] = {
                                "time": values[0],
                                "open": values[1],
                                "close": values[4],
                                "max": values[2],
                                "min": values[3],
                                "volume": round(values[5] * 100) / 100,
                            }
                        continue
                    if key in self._study_listeners:
                        self._study_listeners[key](packet)
                self._handle_event("update", changes)
                return

            if packet.get("type") == "symbol_error":
                self._handle_error(f"({data[1]}) Symbol error:", data[2])
                return

            if packet.get("type") == "series_error":
                self._handle_error("Series error:", data[3] if len(data) > 3 else None)
                return

            if packet.get("type") == "critical_error":
                name = data[1] if len(data) > 1 else None
                description = data[2] if len(data) > 2 else None
                self._handle_error("Critical error:", name, description)

        def _on_replay_data(self, packet):
            if client.get("debug"):
                print("REPLAY SESSION DATA", packet)

            data = packet.get("data", [])
            if packet.get("type") == "replay_ok":
                req_id = data[1] if len(data) > 1 else None
                callback = self._replay_ok_cb.pop(req_id, None)
                if callback:
                    callback()
                return

            if packet.get("type") == "replay_instance_id":
                self._handle_event("replayLoaded", data[1])
                return

            if packet.get("type") == "replay_point":
                self._handle_event("replayPoint", data[1])
                return

            if packet.get("type") == "replay_resolutions":
                self._handle_event("replayResolution", data[1], data[2])
                return

            if packet.get("type") == "replay_data_end":
                self._handle_event("replayEnd")
                return

            if packet.get("type") == "critical_error":
                name = data[1] if len(data) > 1 else None
                description = data[2] if len(data) > 2 else None
                self._handle_error("Critical error:", name, description)

        def setSeries(self, timeframe="240", range=100, reference=None):
            if not self._current_series:
                self._handle_error("Please set the market before setting series")
                return
            calc_range = range if reference is None else ["bar_count", reference, range]
            self._periods = {}
            self._client["send"](
                f"{'modify' if self._series_created else 'create'}_series",
                [
                    self._chart_session_id,
                    "$prices",
                    "s1",
                    f"ser_{self._current_series}",
                    timeframe,
                    "" if self._series_created else calc_range,
                ],
            )
            self._series_created = True

        def setMarket(self, symbol, options=None):
            options = options or {}
            self._periods = {}

            if self._replay_mode:
                self._replay_mode = False
                self._client["send"]("replay_delete_session", [self._replay_session_id])

            symbol_init = {
                "symbol": symbol or "BTCEUR",
                "adjustment": options.get("adjustment", "splits"),
            }
            if options.get("backadjustment"):
                symbol_init["backadjustment"] = "default"
            if options.get("session"):
                symbol_init["session"] = options.get("session")
            if options.get("currency"):
                symbol_init["currency-id"] = options.get("currency")

            if options.get("replay"):
                if not self._replay_mode:
                    self._replay_mode = True
                    self._client["send"]("replay_create_session", [self._replay_session_id])
                self._client["send"](
                    "replay_add_series",
                    [
                        self._replay_session_id,
                        "req_replay_addseries",
                        f"={json.dumps(symbol_init, separators=(',', ':'))}",
                        options.get("timeframe"),
                    ],
                )
                self._client["send"](
                    "replay_reset",
                    [self._replay_session_id, "req_replay_reset", options.get("replay")],
                )

            complex_chart = options.get("type") or options.get("replay")
            chart_init = {} if complex_chart else symbol_init
            if complex_chart:
                if options.get("replay"):
                    chart_init["replay"] = self._replay_session_id
                chart_init["symbol"] = symbol_init
                if options.get("type"):
                    chart_init["type"] = CHART_TYPES.get(options.get("type"))
                    chart_init["inputs"] = dict(options.get("inputs", {}))

            self._current_series += 1

            self._client["send"](
                "resolve_symbol",
                [
                    self._chart_session_id,
                    f"ser_{self._current_series}",
                    f"={json.dumps(chart_init, separators=(',', ':'))}",
                ],
            )

            timeframe = options.get("timeframe") or "240"
            range_value = options.get("range")
            if range_value is None:
                range_value = 100
            self.setSeries(timeframe, range_value, options.get("to"))

        def setTimezone(self, timezone):
            self._periods = {}
            self._client["send"]("switch_timezone", [self._chart_session_id, timezone])

        def fetchMore(self, number=1):
            self._client["send"]("request_more_data", [self._chart_session_id, "$prices", number])

        def replayStep(self, number=1):
            future = Future()
            if not self._replay_mode:
                self._handle_error("No replay session")
                future.set_exception(RuntimeError("No replay session"))
                return future
            req_id = gen_session_id("rsq_step")
            self._client["send"]("replay_step", [self._replay_session_id, req_id, number])
            self._replay_ok_cb[req_id] = lambda: future.set_result(True)
            return future

        def replayStart(self, interval=1000):
            future = Future()
            if not self._replay_mode:
                self._handle_error("No replay session")
                future.set_exception(RuntimeError("No replay session"))
                return future
            req_id = gen_session_id("rsq_start")
            self._client["send"]("replay_start", [self._replay_session_id, req_id, interval])
            self._replay_ok_cb[req_id] = lambda: future.set_result(True)
            return future

        def replayStop(self):
            future = Future()
            if not self._replay_mode:
                self._handle_error("No replay session")
                future.set_exception(RuntimeError("No replay session"))
                return future
            req_id = gen_session_id("rsq_stop")
            self._client["send"]("replay_stop", [self._replay_session_id, req_id])
            self._replay_ok_cb[req_id] = lambda: future.set_result(True)
            return future

        def onSymbolLoaded(self, cb):
            self._callbacks["symbolLoaded"].append(cb)

        def onUpdate(self, cb):
            self._callbacks["update"].append(cb)

        def onReplayLoaded(self, cb):
            self._callbacks["replayLoaded"].append(cb)

        def onReplayResolution(self, cb):
            self._callbacks["replayResolution"].append(cb)

        def onReplayEnd(self, cb):
            self._callbacks["replayEnd"].append(cb)

        def onReplayPoint(self, cb):
            self._callbacks["replayPoint"].append(cb)

        def onError(self, cb):
            self._callbacks["error"].append(cb)

        def onEvent(self, cb):
            self._callbacks["event"].append(cb)

        def delete(self):
            if self._replay_mode:
                self._client["send"]("replay_delete_session", [self._replay_session_id])
            self._client["send"]("chart_delete_session", [self._chart_session_id])
            client["sessions"].pop(self._chart_session_id, None)
            client["sessions"].pop(self._replay_session_id, None)
            self._replay_mode = False

    return ChartSession
