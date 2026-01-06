import platform
import re

import requests

from .classes.pine_indicator import PineIndicator
from .utils import gen_auth_cookies

_VALIDATE_STATUS = lambda status: status < 500

_INDICATORS = ["Recommend.Other", "Recommend.All", "Recommend.MA"]
_BUILTIN_INDIC_LIST = []


def _fetch_scan_data(tickers=None, columns=None):
    tickers = tickers or []
    columns = columns or []
    response = requests.post(
        "https://scanner.tradingview.com/global/scan",
        json={"symbols": {"tickers": tickers}, "columns": columns},
    )
    return response.json()


def getTA(market_id):
    advice = {}
    cols = [
        f"{indicator}|{period}" if period != "1D" else indicator
        for period in ["1", "5", "15", "60", "240", "1D", "1W", "1M"]
        for indicator in _INDICATORS
    ]
    result = _fetch_scan_data([market_id], cols)
    if not result.get("data") or not result["data"][0]:
        return False

    for idx, value in enumerate(result["data"][0].get("d", [])):
        name_period = cols[idx].split("|")
        name = name_period[0]
        period = name_period[1] if len(name_period) > 1 else "1D"
        advice.setdefault(period, {})[name.split(".")[-1]] = round(value * 1000) / 500

    return advice


def searchMarket(search, filter=""):
    response = requests.get(
        "https://symbol-search.tradingview.com/symbol_search",
        params={"text": search.replace(" ", "%20"), "type": filter},
        headers={"origin": "https://www.tradingview.com"},
    )
    data = response.json()
    results = []
    for item in data:
        exchange = item.get("exchange", "").split(" ")[0]
        market_id = f"{exchange}:{item.get('symbol')}"

        def _get_ta(mid=market_id):
            return getTA(mid)

        results.append(
            {
                "id": market_id,
                "exchange": exchange,
                "fullExchange": item.get("exchange"),
                "symbol": item.get("symbol"),
                "description": item.get("description"),
                "type": item.get("type"),
                "getTA": _get_ta,
            }
        )
    return results


def searchMarketV3(search, filter="", offset=0):
    parts = search.upper().replace(" ", "+").split(":")
    response = requests.get(
        "https://symbol-search.tradingview.com/symbol_search/v3",
        params={
            "exchange": parts[0] if len(parts) == 2 else None,
            "text": parts[-1],
            "search_type": filter,
            "start": offset,
        },
        headers={"origin": "https://www.tradingview.com"},
    )
    data = response.json()
    results = []
    for item in data.get("symbols", []):
        exchange = item.get("exchange", "").split(" ")[0]
        market_id = (
            f"{item.get('prefix')}:{item.get('symbol')}"
            if item.get("prefix")
            else f"{exchange.upper()}:{item.get('symbol')}"
        )

        def _get_ta(mid=market_id):
            return getTA(mid)

        results.append(
            {
                "id": market_id,
                "exchange": exchange,
                "fullExchange": item.get("exchange"),
                "symbol": item.get("symbol"),
                "description": item.get("description"),
                "type": item.get("type"),
                "getTA": _get_ta,
            }
        )
    return results


def searchIndicator(search=""):
    if not _BUILTIN_INDIC_LIST:
        for ind_type in ["standard", "candlestick", "fundamental"]:
            response = requests.get(
                "https://pine-facade.tradingview.com/pine-facade/list",
                params={"filter": ind_type},
            )
            _BUILTIN_INDIC_LIST.extend(response.json())

    response = requests.get(
        "https://www.tradingview.com/pubscripts-suggest-json",
        params={"search": search.replace(" ", "%20")},
    )

    def norm(text=""):
        return re.sub(r"[^A-Z]", "", text.upper())

    results = []
    search_norm = norm(search)
    for ind in _BUILTIN_INDIC_LIST:
        if search_norm in norm(ind.get("scriptName", "")) or search_norm in norm(ind.get("extra", {}).get("shortDescription", "")):
            script_id = ind.get("scriptIdPart")

            def _get(script=script_id, version=ind.get("version")):
                return getIndicator(script, version)

            results.append(
                {
                    "id": script_id,
                    "version": ind.get("version"),
                    "name": ind.get("scriptName"),
                    "author": {"id": ind.get("userId"), "username": "@TRADINGVIEW@"},
                    "image": "",
                    "access": "closed_source",
                    "source": "",
                    "type": ind.get("extra", {}).get("kind", "study"),
                    "get": _get,
                }
            )

    for ind in response.json().get("results", []):
        script_id = ind.get("scriptIdPart")

        def _get(script=script_id, version=ind.get("version")):
            return getIndicator(script, version)

        results.append(
            {
                "id": script_id,
                "version": ind.get("version"),
                "name": ind.get("scriptName"),
                "author": {
                    "id": ind.get("author", {}).get("id"),
                    "username": ind.get("author", {}).get("username"),
                },
                "image": ind.get("imageUrl"),
                "access": ["open_source", "closed_source", "invite_only"][ind.get("access", 0) - 1]
                if ind.get("access")
                else "other",
                "source": ind.get("scriptSource"),
                "type": ind.get("extra", {}).get("kind", "study"),
                "get": _get,
            }
        )

    return results


def getIndicator(indicator_id, version="last", session="", signature=""):
    indic_id = re.sub(r"[ %]", "%25", indicator_id)
    response = requests.get(
        f"https://pine-facade.tradingview.com/pine-facade/translate/{indic_id}/{version}",
        headers={"cookie": gen_auth_cookies(session, signature)},
    )
    data = response.json()

    meta = data.get("result", {}).get("metaInfo")
    if not data.get("success") or not meta or not meta.get("inputs"):
        raise ValueError(f"Inexistent or unsupported indicator: '{data.get('reason')}'")

    inputs = {}
    for input_item in meta.get("inputs", []):
        if input_item.get("id") in ("text", "pineId", "pineVersion"):
            continue
        inline_name = re.sub(r"[^a-zA-Z0-9_]", "", input_item.get("name", "").replace(" ", "_"))
        inputs[input_item.get("id")] = {
            "name": input_item.get("name"),
            "inline": input_item.get("inline") or inline_name,
            "internalID": input_item.get("internalID") or inline_name,
            "tooltip": input_item.get("tooltip"),
            "type": input_item.get("type"),
            "value": input_item.get("defval"),
            "isHidden": bool(input_item.get("isHidden")),
            "isFake": bool(input_item.get("isFake")),
        }
        if input_item.get("options"):
            inputs[input_item.get("id")]["options"] = input_item.get("options")

    plots = {}
    for plot_id, style in meta.get("styles", {}).items():
        plot_title = re.sub(r"[^a-zA-Z0-9_]", "", style.get("title", "").replace(" ", "_"))
        titles = set(plots.values())
        if plot_title in titles:
            idx = 2
            while f"{plot_title}_{idx}" in titles:
                idx += 1
            plots[plot_id] = f"{plot_title}_{idx}"
        else:
            plots[plot_id] = plot_title

    for plot in meta.get("plots", []):
        if not plot.get("target"):
            continue
        target_name = plots.get(plot.get("target"), plot.get("target"))
        plots[plot.get("id")] = f"{target_name}_{plot.get('type')}"

    return PineIndicator(
        {
            "pineId": meta.get("scriptIdPart") or indic_id,
            "pineVersion": meta.get("pine", {}).get("version") or version,
            "description": meta.get("description"),
            "shortDescription": meta.get("shortDescription"),
            "inputs": inputs,
            "plots": plots,
            "script": data.get("result", {}).get("ilTemplate"),
        }
    )


def loginUser(username, password, remember=True, UA="TWAPI/3.0"):
    response = requests.post(
        "https://www.tradingview.com/accounts/signin/",
        data=f"username={username}&password={password}{'&remember=on' if remember else ''}",
        headers={
            "referer": "https://www.tradingview.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-agent": f"{UA} ({platform.version()}; {platform.system().lower()}; {platform.machine()})",
        },
    )
    data = response.json()
    if data.get("error"):
        raise ValueError(data.get("error"))

    session = response.cookies.get("sessionid")
    signature = response.cookies.get("sessionid_sign")

    return {
        "id": data.get("user", {}).get("id"),
        "username": data.get("user", {}).get("username"),
        "firstName": data.get("user", {}).get("first_name"),
        "lastName": data.get("user", {}).get("last_name"),
        "reputation": data.get("user", {}).get("reputation"),
        "following": data.get("user", {}).get("following"),
        "followers": data.get("user", {}).get("followers"),
        "notifications": data.get("user", {}).get("notification_count"),
        "session": session,
        "signature": signature,
        "sessionHash": data.get("user", {}).get("session_hash"),
        "privateChannel": data.get("user", {}).get("private_channel"),
        "authToken": data.get("user", {}).get("auth_token"),
        "joinDate": _parse_datetime(data.get("user", {}).get("date_joined")),
    }


def _parse_datetime(text):
    if not text:
        return None
    if text.endswith("Z"):
        text = text.replace("Z", "+00:00")
    try:
        from datetime import datetime

        return datetime.fromisoformat(text)
    except ValueError:
        return text


def getUser(session, signature="", location="https://www.tradingview.com/"):
    response = requests.get(
        location,
        headers={"cookie": gen_auth_cookies(session, signature)},
        allow_redirects=False,
    )
    data = response.text

    if "auth_token" in data:
        def _extract(pattern, cast=None):
            match = re.search(pattern, data)
            if not match:
                return None
            value = match.group(1)
            if cast:
                try:
                    return cast(value)
                except ValueError:
                    return cast()
            return value

        return {
            "id": _extract(r'"id":([0-9]{1,10}),', int),
            "username": _extract(r'"username":"(.*?)"'),
            "firstName": _extract(r'"first_name":"(.*?)"'),
            "lastName": _extract(r'"last_name":"(.*?)"'),
            "reputation": _extract(r'"reputation":(.*?),', float) or 0,
            "following": _extract(r',"following":([0-9]*?),', float) or 0,
            "followers": _extract(r',"followers":([0-9]*?),', float) or 0,
            "notifications": {
                "following": _extract(r'"notification_count":\{"following":([0-9]*),', float) or 0,
                "user": _extract(r'"notification_count":\{"following":[0-9]*,"user":([0-9]*)', float) or 0,
            },
            "session": session,
            "signature": signature,
            "sessionHash": _extract(r'"session_hash":"(.*?)"'),
            "privateChannel": _extract(r'"private_channel":"(.*?)"'),
            "authToken": _extract(r'"auth_token":"(.*?)"'),
            "joinDate": _parse_datetime(_extract(r'"date_joined":"(.*?)"')),
        }

    redirect = response.headers.get("location")
    if redirect and redirect != location:
        return getUser(session, signature, redirect)

    raise ValueError("Wrong or expired sessionid/signature")


def getPrivateIndicators(session, signature=""):
    response = requests.get(
        "https://pine-facade.tradingview.com/pine-facade/list",
        headers={"cookie": gen_auth_cookies(session, signature)},
        params={"filter": "saved"},
    )
    data = response.json()
    results = []
    for ind in data:
        script_id = ind.get("scriptIdPart")

        def _get(script=script_id, version=ind.get("version")):
            return getIndicator(script, version, session, signature)

        results.append(
            {
                "id": script_id,
                "version": ind.get("version"),
                "name": ind.get("scriptName"),
                "author": {"id": -1, "username": "@ME@"},
                "image": ind.get("imageUrl"),
                "access": "private",
                "source": ind.get("scriptSource"),
                "type": ind.get("extra", {}).get("kind", "study"),
                "get": _get,
            }
        )
    return results


def getChartToken(layout, credentials=None):
    credentials = credentials or {}
    if credentials.get("id") and credentials.get("session"):
        user_id = credentials.get("id")
        session = credentials.get("session")
        signature = credentials.get("signature")
    else:
        user_id = -1
        session = None
        signature = None

    response = requests.get(
        "https://www.tradingview.com/chart-token",
        headers={"cookie": gen_auth_cookies(session, signature)},
        params={"image_url": layout, "user_id": user_id},
    )
    data = response.json()
    if not data.get("token"):
        raise ValueError("Wrong layout or credentials")
    return data.get("token")


def getDrawings(layout, symbol="", credentials=None, chart_id="_shared"):
    token = getChartToken(layout, credentials or {})
    response = requests.get(
        f"https://charts-storage.tradingview.com/charts-storage/get/layout/{layout}/sources",
        params={"chart_id": chart_id, "jwt": token, "symbol": symbol},
    )
    data = response.json()
    if not data.get("payload"):
        raise ValueError("Wrong layout, user credentials, or chart id.")

    drawings = []
    for drawing in (data.get("payload", {}).get("sources", {}) or {}).values():
        merged = dict(drawing)
        merged.update(drawing.get("state", {}))
        drawings.append(merged)
    return drawings
