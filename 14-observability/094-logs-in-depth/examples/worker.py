"""A background worker: processes an order every half second, and reports every 5th one as failed."""
import sys
import time

order = 0
while True:
    order += 1
    if order % 5 == 0:
        print(f"ERROR order {order}: payment declined", file=sys.stderr)
    else:
        print(f"INFO order {order}: processed")
    time.sleep(0.5)
