"""A cache with a bug: it keeps every entry forever, so memory grows by 8 MB every half second.

Set MAX_ENTRIES to keep only the newest entries (the fix): memory then stays constant.
"""
import os
import time

max_entries = int(os.environ.get("MAX_ENTRIES", "0"))  # 0 = unbounded (the bug)
cache = []
while True:
    cache.append(b"x" * (8 * 1024 * 1024))  # one 8 MB entry, filled, so it really uses memory
    if max_entries and len(cache) > max_entries:
        cache.pop(0)
    print(f"cache holds {len(cache) * 8} MB", flush=True)
    time.sleep(0.5)
