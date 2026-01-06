import time

_DEFAULT_VALUES = {
    "Volume@tv-basicstudies-241": {
        "length": 20,
        "col_prev_close": False,
    },
    "VbPFixed@tv-basicstudies-241": {
        "rowsLayout": "Number Of Rows",
        "rows": 24,
        "volume": "Up/Down",
        "vaVolume": 70,
        "subscribeRealtime": False,
        "first_bar_time": float("nan"),
        "last_bar_time": int(time.time() * 1000),
        "extendToRight": False,
        "mapRightBoundaryToBarStartTime": True,
    },
    "VbPFixed@tv-basicstudies-241!": {
        "rowsLayout": "Number Of Rows",
        "rows": 24,
        "volume": "Up/Down",
        "vaVolume": 70,
        "subscribeRealtime": False,
        "first_bar_time": float("nan"),
        "last_bar_time": int(time.time() * 1000),
    },
    "VbPFixed@tv-volumebyprice-53!": {
        "rowsLayout": "Number Of Rows",
        "rows": 24,
        "volume": "Up/Down",
        "vaVolume": 70,
        "subscribeRealtime": False,
        "first_bar_time": float("nan"),
        "last_bar_time": int(time.time() * 1000),
    },
    "VbPSessions@tv-volumebyprice-53": {
        "rowsLayout": "Number Of Rows",
        "rows": 24,
        "volume": "Up/Down",
        "vaVolume": 70,
        "extendPocRight": False,
    },
    "VbPSessionsRough@tv-volumebyprice-53!": {
        "volume": "Up/Down",
        "vaVolume": 70,
    },
    "VbPSessionsDetailed@tv-volumebyprice-53!": {
        "volume": "Up/Down",
        "vaVolume": 70,
        "subscribeRealtime": False,
        "first_visible_bar_time": float("nan"),
        "last_visible_bar_time": int(time.time() * 1000),
    },
    "VbPVisible@tv-volumebyprice-53": {
        "rowsLayout": "Number Of Rows",
        "rows": 24,
        "volume": "Up/Down",
        "vaVolume": 70,
        "subscribeRealtime": False,
        "first_visible_bar_time": float("nan"),
        "last_visible_bar_time": int(time.time() * 1000),
    },
}


class BuiltInIndicator:
    def __init__(self, indicator_type=""):
        if not indicator_type:
            raise ValueError(f"Wrong built-in indicator type '{indicator_type}'.")
        self._type = indicator_type
        self._options = dict(_DEFAULT_VALUES.get(indicator_type, {}))

    @property
    def type(self):
        return self._type

    @property
    def options(self):
        return self._options

    def setOption(self, key, value, FORCE=False):
        if FORCE:
            self._options[key] = value
            return

        default_options = _DEFAULT_VALUES.get(self._type, {})
        if key in default_options:
            required_type = type(default_options[key])
            if required_type is float:
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    raise TypeError(
                        f"Wrong '{key}' value type '{type(value).__name__}' (must be '{required_type.__name__}')"
                    )
            elif not isinstance(value, required_type):
                raise TypeError(
                    f"Wrong '{key}' value type '{type(value).__name__}' (must be '{required_type.__name__}')"
                )
        elif self._type in _DEFAULT_VALUES:
            raise ValueError(f"Option '{key}' is denied with '{self._type}' indicator")

        self._options[key] = value
