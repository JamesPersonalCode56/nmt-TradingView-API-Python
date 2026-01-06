import json

from ..protocol import parse_compressed
from ..utils import gen_session_id
from .graphic_parser import graphic_parse
from ..classes.pine_indicator import PineIndicator
from ..classes.builtin_indicator import BuiltInIndicator


def _get_inputs(options):
    if isinstance(options, PineIndicator):
        pine_inputs = {"text": options.script}
        if options.pineId:
            pine_inputs["pineId"] = options.pineId
        if options.pineVersion:
            pine_inputs["pineVersion"] = options.pineVersion
        for idx, input_id in enumerate(options.inputs or {}):
            input_item = options.inputs[input_id]
            pine_inputs[input_id] = {
                "v": input_item.get("value") if input_item.get("type") != "color" else idx,
                "f": bool(input_item.get("isFake")),
                "t": input_item.get("type"),
            }
        return pine_inputs
    return options.options


def _parse_trades(trades):
    return [
        {
            "entry": {
                "name": trade["e"]["c"],
                "type": "short" if trade["e"]["tp"][0] == "s" else "long",
                "value": trade["e"]["p"],
                "time": trade["e"]["tm"],
            },
            "exit": {
                "name": trade["x"]["c"],
                "value": trade["x"]["p"],
                "time": trade["x"]["tm"],
            },
            "quantity": trade.get("q"),
            "profit": trade.get("tp"),
            "cumulative": trade.get("cp"),
            "runup": trade.get("rn"),
            "drawdown": trade.get("dd"),
        }
        for trade in reversed(trades)
    ]


def study_constructor(chart_session):
    class ChartStudy:
        def __init__(self, indicator):
            if not isinstance(indicator, (PineIndicator, BuiltInIndicator)):
                raise ValueError(
                    "Indicator argument must be an instance of PineIndicator or BuiltInIndicator."
                    " Please use 'TradingView.getIndicator(...)' function."
                )

            self._stud_id = gen_session_id("st")
            self._study_listeners = chart_session["studyListeners"]
            self._periods = {}
            self._indexes = []
            self._graphic = {}
            self._strategy_report = {
                "trades": [],
                "history": {},
                "performance": {},
            }
            self._callbacks = {
                "studyCompleted": [],
                "update": [],
                "event": [],
                "error": [],
            }

            self.instance = indicator

            def on_data(packet):
                if chart_session.get("debug"):
                    print("STUDY DATA", packet)

                if packet.get("type") == "study_completed":
                    self._handle_event("studyCompleted")
                    return

                if packet.get("type") in ("timescale_update", "du"):
                    changes = []
                    payload = packet.get("data", [])
                    payload_body = payload[1] if len(payload) > 1 else {}
                    data = payload_body.get(self._stud_id) if isinstance(payload_body, dict) else None
                    if data and data.get("st"):
                        for period in data.get("st", []):
                            out = {}
                            plots = getattr(self.instance, "plots", None)
                            for i, plot in enumerate(period.get("v", [])):
                                if not plots:
                                    out["$time" if i == 0 else f"plot_{i - 1}"] = plot
                                    continue
                                plot_name = (
                                    "$time" if i == 0 else plots.get(f"plot_{i - 1}")
                                )
                                if plot_name and plot_name not in out:
                                    out[plot_name] = plot
                                else:
                                    out[f"plot_{i - 1}"] = plot
                            self._periods[period.get("v", [None])[0]] = out
                        changes.append("plots")

                    ns = data.get("ns") if data else None
                    if ns and ns.get("d"):
                        parsed = json.loads(ns.get("d"))
                        if parsed.get("graphicsCmds"):
                            graphics = parsed.get("graphicsCmds")
                            if graphics.get("erase"):
                                for instruction in graphics.get("erase", []):
                                    if instruction.get("action") == "all":
                                        if not instruction.get("type"):
                                            for draw_type in list(self._graphic.keys()):
                                                self._graphic[draw_type] = {}
                                        else:
                                            self._graphic.pop(instruction.get("type"), None)
                                    elif instruction.get("action") == "one":
                                        draw_type = instruction.get("type")
                                        draw_id = instruction.get("id")
                                        if draw_type in self._graphic:
                                            self._graphic[draw_type].pop(draw_id, None)

                            if graphics.get("create"):
                                for draw_type, groups in graphics.get("create", {}).items():
                                    self._graphic.setdefault(draw_type, {})
                                    for group in groups:
                                        for item in group.get("data", []):
                                            self._graphic[draw_type][item.get("id")] = item

                            changes.append("graphic")

                        def update_report(report):
                            if report.get("currency"):
                                self._strategy_report["currency"] = report.get("currency")
                                changes.append("report.currency")
                            if report.get("settings"):
                                self._strategy_report["settings"] = report.get("settings")
                                changes.append("report.settings")
                            if report.get("performance"):
                                self._strategy_report["performance"] = report.get("performance")
                                changes.append("report.perf")
                            if report.get("trades"):
                                self._strategy_report["trades"] = _parse_trades(report.get("trades"))
                                changes.append("report.trades")
                            if report.get("equity"):
                                self._strategy_report["history"] = {
                                    "buyHold": report.get("buyHold"),
                                    "buyHoldPercent": report.get("buyHoldPercent"),
                                    "drawDown": report.get("drawDown"),
                                    "drawDownPercent": report.get("drawDownPercent"),
                                    "equity": report.get("equity"),
                                    "equityPercent": report.get("equityPercent"),
                                }
                                changes.append("report.history")

                        if parsed.get("dataCompressed"):
                            try:
                                report = parse_compressed(parsed.get("dataCompressed")).get("report", {})
                                update_report(report)
                            except Exception as exc:
                                self._handle_error("Compressed data parse error", str(exc))

                        if parsed.get("data", {}).get("report"):
                            update_report(parsed.get("data", {}).get("report"))

                    if ns and isinstance(ns.get("indexes"), list):
                        self._indexes = ns.get("indexes")

                    self._handle_event("update", changes)
                    return

                if packet.get("type") == "study_error":
                    data = packet.get("data", [])
                    self._handle_error(data[3] if len(data) > 3 else None, data[4] if len(data) > 4 else None)

            self._study_listeners[self._stud_id] = on_data

            chart_session["send"](
                "create_study",
                [
                    chart_session["sessionID"],
                    f"{self._stud_id}",
                    "st1",
                    "$prices",
                    self.instance.type,
                    _get_inputs(self.instance),
                ],
            )

        @property
        def periods(self):
            return sorted(self._periods.values(), key=lambda v: v.get("$time", 0), reverse=True)

        @property
        def graphic(self):
            translator = {}
            indexes = chart_session.get("indexes", {})
            for n, key in enumerate(sorted(indexes, key=lambda k: indexes[k], reverse=True)):
                translator[str(key)] = n
            mapped = [translator.get(str(i)) for i in self._indexes]
            return graphic_parse(self._graphic, mapped)

        @property
        def strategyReport(self):
            return self._strategy_report

        def setIndicator(self, indicator):
            if not isinstance(indicator, (PineIndicator, BuiltInIndicator)):
                raise ValueError(
                    "Indicator argument must be an instance of PineIndicator or BuiltInIndicator."
                    " Please use 'TradingView.getIndicator(...)' function."
                )
            self.instance = indicator
            chart_session["send"](
                "modify_study",
                [
                    chart_session["sessionID"],
                    f"{self._stud_id}",
                    "st1",
                    _get_inputs(self.instance),
                ],
            )

        def onReady(self, cb):
            self._callbacks["studyCompleted"].append(cb)

        def onUpdate(self, cb):
            self._callbacks["update"].append(cb)

        def onError(self, cb):
            self._callbacks["error"].append(cb)

        def onEvent(self, cb):
            self._callbacks["event"].append(cb)

        def remove(self):
            chart_session["send"]("remove_study", [chart_session["sessionID"], self._stud_id])
            self._study_listeners.pop(self._stud_id, None)

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

    return ChartStudy
