#!/usr/bin/env bash
# locked.sh COMMAND [ARG ...]: run a command while holding the test lock (tests/.lock).
#
# The test runner empties the Docker engine before and after every lesson file. Anything you try out by hand on the
# same engine while a test run is going would be removed under your feet (and could break that run), so experiments
# go through this script:
#
#   bash tests/locked.sh bash -c 'docker run --rm alpine:3.23 echo hi'
#
# A run that was killed can leave the lock behind: remove tests/.lock if no test run is going.
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
lock="$root/tests/.lock"
until mkdir "$lock" 2> /dev/null; do
  echo "waiting for another test run to finish ($lock)" >&2
  sleep 10
done
trap 'rm -rf "$lock"' EXIT
export MSYS_NO_PATHCONV=1
"$@"
