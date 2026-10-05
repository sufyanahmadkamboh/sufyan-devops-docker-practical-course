#!/bin/sh
# take-order.sh ITEM: record an order in the order log and show the log
set -eu
echo "$(date -u +%H:%M:%S) ${1:-espresso}" >> "${ORDER_LOG:-/app/orders.log}"
cat "${ORDER_LOG:-/app/orders.log}"
