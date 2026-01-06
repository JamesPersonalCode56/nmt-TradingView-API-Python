import base64
import io
import json
import re
import zipfile

_CLEANER = re.compile(r"~h~")
_SPLITTER = re.compile(r"~m~\d+~m~")


def parse_ws_packet(message):
    if isinstance(message, (bytes, bytearray)):
        message = message.decode("utf-8", errors="ignore")
    cleaned = _CLEANER.sub("", message)
    parts = _SPLITTER.split(cleaned)
    packets = []
    for part in parts:
        if not part:
            continue
        try:
            packets.append(json.loads(part))
        except json.JSONDecodeError:
            print("Cant parse", part)
    return packets


def format_ws_packet(packet):
    if isinstance(packet, (dict, list)):
        msg = json.dumps(packet, separators=(",", ":"))
    else:
        msg = str(packet)
    return f"~m~{len(msg)}~m~{msg}"


def parse_compressed(data):
    if isinstance(data, str):
        raw = base64.b64decode(data)
    else:
        raw = base64.b64decode(data)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
        if not names:
            raise ValueError("Empty compressed payload")
        name = names[0]
        payload = zf.read(name).decode("utf-8")
    return json.loads(payload)
