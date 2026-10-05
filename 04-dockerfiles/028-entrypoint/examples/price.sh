#!/bin/sh
# price.sh ITEM: print the price of a menu item
set -eu
item="${1:?usage: price ITEM}"
line=$(grep -i "^$item," /app/menu.csv) || { echo "unknown item: $item" >&2; exit 1; }
echo "${line#*,} EUR"
