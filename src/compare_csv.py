import csv
import math

TV_FILE = "candles_15m.csv"
BN_FILE = "candles_15m_binance.csv"
REPORT_FILE = "candles_15m_diff_report.csv"
SUMMARY_FILE = "candles_15m_diff_summary.csv"

FIELDS = ["open", "high", "low", "close", "volume"]


def load_csv(path):
    data = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = row.get("datetime")
            if not dt:
                continue
            entry = {"datetime": dt}
            for field in FIELDS:
                val = row.get(field)
                entry[field] = float(val) if val is not None and val != "" else None
            data[dt] = entry
    return data


def pct_diff(a, b):
    if b == 0:
        return 0.0 if a == 0 else math.inf
    return abs(a - b) / abs(b) * 100.0


def main():
    tv = load_csv(TV_FILE)
    bn = load_csv(BN_FILE)

    tv_keys = set(tv.keys())
    bn_keys = set(bn.keys())
    common = sorted(tv_keys & bn_keys)
    only_tv = sorted(tv_keys - bn_keys)
    only_bn = sorted(bn_keys - tv_keys)

    summary = {
        field: {
            "count": 0,
            "sum_abs": 0.0,
            "sum_pct": 0.0,
            "max_abs": 0.0,
            "max_pct": 0.0,
        }
        for field in FIELDS
    }

    with open(REPORT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "datetime",
                "field",
                "tradingview",
                "binance",
                "abs_diff",
                "pct_diff",
            ]
        )

        for dt in common:
            tv_row = tv[dt]
            bn_row = bn[dt]
            for field in FIELDS:
                tv_val = tv_row.get(field)
                bn_val = bn_row.get(field)
                if tv_val is None or bn_val is None:
                    continue
                abs_diff = abs(tv_val - bn_val)
                pct = pct_diff(tv_val, bn_val)

                writer.writerow([dt, field, tv_val, bn_val, abs_diff, pct])

                stats = summary[field]
                stats["count"] += 1
                stats["sum_abs"] += abs_diff
                if not math.isinf(pct):
                    stats["sum_pct"] += pct
                stats["max_abs"] = max(stats["max_abs"], abs_diff)
                stats["max_pct"] = max(stats["max_pct"], pct)

    with open(SUMMARY_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["field", "count", "avg_abs", "max_abs", "avg_pct", "max_pct"])
        for field, stats in summary.items():
            count = stats["count"]
            avg_abs = stats["sum_abs"] / count if count else 0.0
            avg_pct = stats["sum_pct"] / count if count else 0.0
            writer.writerow(
                [
                    field,
                    count,
                    avg_abs,
                    stats["max_abs"],
                    avg_pct,
                    stats["max_pct"],
                ]
            )

    print("Report saved:", REPORT_FILE)
    print("Summary saved:", SUMMARY_FILE)
    if only_tv:
        print("Only in TradingView:", len(only_tv))
    if only_bn:
        print("Only in Binance:", len(only_bn))


if __name__ == "__main__":
    main()
