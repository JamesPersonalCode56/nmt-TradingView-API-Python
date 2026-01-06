TRANSLATOR = {
    "extend": {
        "r": "right",
        "l": "left",
        "b": "both",
        "n": "none",
    },
    "yLoc": {
        "pr": "price",
        "ab": "abovebar",
        "bl": "belowbar",
    },
    "labelStyle": {
        "n": "none",
        "xcr": "xcross",
        "cr": "cross",
        "tup": "triangleup",
        "tdn": "triangledown",
        "flg": "flag",
        "cir": "circle",
        "aup": "arrowup",
        "adn": "arrowdown",
        "lup": "label_up",
        "ldn": "label_down",
        "llf": "label_left",
        "lrg": "label_right",
        "llwlf": "label_lower_left",
        "llwrg": "label_lower_right",
        "luplf": "label_upper_left",
        "luprg": "label_upper_right",
        "lcn": "label_center",
        "sq": "square",
        "dia": "diamond",
    },
    "lineStyle": {
        "sol": "solid",
        "dot": "dotted",
        "dsh": "dashed",
        "al": "arrow_left",
        "ar": "arrow_right",
        "ab": "arrow_both",
    },
    "boxStyle": {
        "sol": "solid",
        "dot": "dotted",
        "dsh": "dashed",
    },
}


def graphic_parse(raw_graphic=None, indexes=None):
    raw_graphic = raw_graphic or {}
    indexes = indexes or []

    def safe_index(value):
        if value is None:
            return None
        if isinstance(value, int) and value < len(indexes):
            return indexes[value]
        return None

    return {
        "labels": [
            {
                "id": label.get("id"),
                "x": safe_index(label.get("x")),
                "y": label.get("y"),
                "yLoc": TRANSLATOR["yLoc"].get(label.get("yl"), label.get("yl")),
                "text": label.get("t"),
                "style": TRANSLATOR["labelStyle"].get(label.get("st"), label.get("st")),
                "color": label.get("ci"),
                "textColor": label.get("tci"),
                "size": label.get("sz"),
                "textAlign": label.get("ta"),
                "toolTip": label.get("tt"),
            }
            for label in (raw_graphic.get("dwglabels") or {}).values()
        ],
        "lines": [
            {
                "id": line.get("id"),
                "x1": safe_index(line.get("x1")),
                "y1": line.get("y1"),
                "x2": safe_index(line.get("x2")),
                "y2": line.get("y2"),
                "extend": TRANSLATOR["extend"].get(line.get("ex"), line.get("ex")),
                "style": TRANSLATOR["lineStyle"].get(line.get("st"), line.get("st")),
                "color": line.get("ci"),
                "width": line.get("w"),
            }
            for line in (raw_graphic.get("dwglines") or {}).values()
        ],
        "boxes": [
            {
                "id": box.get("id"),
                "x1": safe_index(box.get("x1")),
                "y1": box.get("y1"),
                "x2": safe_index(box.get("x2")),
                "y2": box.get("y2"),
                "color": box.get("c"),
                "bgColor": box.get("bc"),
                "extend": TRANSLATOR["extend"].get(box.get("ex"), box.get("ex")),
                "style": TRANSLATOR["boxStyle"].get(box.get("st"), box.get("st")),
                "width": box.get("w"),
                "text": box.get("t"),
                "textSize": box.get("ts"),
                "textColor": box.get("tc"),
                "textVAlign": box.get("tva"),
                "textHAlign": box.get("tha"),
                "textWrap": box.get("tw"),
            }
            for box in (raw_graphic.get("dwgboxes") or {}).values()
        ],
        "tables": [
            {
                "id": table.get("id"),
                "position": table.get("pos"),
                "rows": table.get("rows"),
                "columns": table.get("cols"),
                "bgColor": table.get("bgc"),
                "frameColor": table.get("frmc"),
                "frameWidth": table.get("frmw"),
                "borderColor": table.get("brdc"),
                "borderWidth": table.get("brdw"),
                "cells": (lambda tid=table.get("id"): _table_cells(raw_graphic, tid)),
            }
            for table in (raw_graphic.get("dwgtables") or {}).values()
        ],
        "horizLines": [
            {
                **hline,
                "startIndex": safe_index(hline.get("startIndex")),
                "endIndex": safe_index(hline.get("endIndex")),
            }
            for hline in (raw_graphic.get("horizlines") or {}).values()
        ],
        "polygons": [
            {
                **poly,
                "points": [
                    {**pt, "index": safe_index(pt.get("index"))}
                    for pt in poly.get("points", [])
                ],
            }
            for poly in (raw_graphic.get("polygons") or {}).values()
        ],
        "horizHists": [
            {
                **hhist,
                "firstBarTime": safe_index(hhist.get("firstBarTime")),
                "lastBarTime": safe_index(hhist.get("lastBarTime")),
            }
            for hhist in (raw_graphic.get("hhists") or {}).values()
        ],
        "raw": lambda: raw_graphic,
    }


def _table_cells(raw_graphic, table_id):
    matrix = []
    for cell in (raw_graphic.get("dwgtablecells") or {}).values():
        if cell.get("tid") != table_id:
            continue
        row = cell.get("row")
        col = cell.get("col")
        if row is None or col is None:
            continue
        while len(matrix) <= row:
            matrix.append([])
        while len(matrix[row]) <= col:
            matrix[row].append(None)
        matrix[row][col] = {
            "id": cell.get("id"),
            "text": cell.get("t"),
            "width": cell.get("w"),
            "height": cell.get("h"),
            "textColor": cell.get("tc"),
            "textHAlign": cell.get("tha"),
            "textVAlign": cell.get("tva"),
            "textSize": cell.get("ts"),
            "bgColor": cell.get("bgc"),
        }
    return matrix
