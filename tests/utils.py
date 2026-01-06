import time


def wait(ms):
    time.sleep(ms / 1000.0)


def calculate_time_gap(periods):
    min_gap = float("inf")
    for i in range(1, len(periods)):
        min_gap = min(min_gap, periods[i - 1]["time"] - periods[i]["time"])
    return min_gap


def wait_for(predicate, timeout=10, interval=0.1):
    end = time.time() + timeout
    while time.time() < end:
        if predicate():
            return True
        time.sleep(interval)
    return False
