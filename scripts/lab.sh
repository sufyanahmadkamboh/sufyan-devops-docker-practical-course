#!/usr/bin/env bash
# lab.sh NAME [SOURCE ...]: create a fresh practice folder ~/docker-practice/NAME for a lesson.
#
# Each SOURCE (a folder of the course, such as examples/node-api or a lesson's examples/before) is copied into it:
# one SOURCE → its contents become the lab folder; several → each one becomes a sub-folder with its own name.
# An existing lab folder of the same name is replaced. Run it from the course folder:
#
#   bash scripts/lab.sh lesson-040 examples/node-api
set -euo pipefail

name="${1:?usage: lab.sh NAME [SOURCE ...]}"
shift
course=$(cd "$(dirname "$0")/.." && pwd)
lab="$HOME/docker-practice/$name"
rm -rf "$lab"
mkdir -p "$lab"
if [ $# -eq 1 ]; then
  cp -r "$course/$1/." "$lab/"
else
  for source in "$@"; do
    cp -r "$course/$source" "$lab/$(basename "$source")"
  done
fi
echo "lab ready: ~/docker-practice/$name"
