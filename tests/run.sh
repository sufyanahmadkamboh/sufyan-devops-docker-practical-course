#!/usr/bin/env bash
# Run lessons exactly as a learner types them, but in a sandbox:
#   * a fresh HOME (your ~/docker-practice, ~/.docker and ~/.kube are never touched)
#   * a separate Docker CLI configuration (docker login in a lesson never stores anything in your real ~/.docker)
#   * every lesson file starts and ends with an empty Docker engine (images stay cached: see tests/mdrun.py)
#   * one run at a time: Docker is shared, so a second run waits for the first one (tests/.lock)
#
#   bash tests/run.sh [--update] [--record DIR] FILE.md [FILE.md ...]
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
py=python3
command -v python3 > /dev/null 2>&1 && python3 -c "" > /dev/null 2>&1 || py=python

# one run at a time: lessons use fixed container names and ports on the one Docker engine
lock="$root/tests/.lock"
until mkdir "$lock" 2> /dev/null; do
  echo "waiting for another test run to finish ($lock)" >&2
  sleep 10
done
trap 'rm -rf "$lock"' EXIT

# the sandbox must be under a path Docker Desktop can bind-mount (C:\Users\... on Windows, anywhere on Linux)
mkdir -p "$root/tests/out"
if pwd -W > /dev/null 2>&1; then lab_home=$(mktemp -d "$root/tests/out/home.XXXXXX"); else lab_home=$(mktemp -d); fi
if pwd -W > /dev/null 2>&1; then masked=$(cd "$lab_home" && pwd -W); else masked=$lab_home; fi

export HOME="$lab_home" MDRUN_HOME="$masked" MDRUN_HOME_POSIX="posix:$lab_home"  # the prefix stops MSYS from converting the path
export DOCKER_CONFIG="$lab_home/.docker"
mkdir -p "$DOCKER_CONFIG" "$lab_home/.kube" && export KUBECONFIG="$lab_home/.kube/config"
# the lessons run from a copy of the course (without .git, videos and earlier test output)
work="$lab_home/docker-practical-course"
mkdir -p "$work"
(cd "$root" && tar --exclude=./.git --exclude=./video --exclude=./tests/out --exclude=./tests/.lock -cf - .) | tar -xf - -C "$work"
export MDRUN_CWD="posix:$work"
# a tools folder next to the course (kind, kubectl, helm on the author's computer), if there is one
if [ -d "$root/../.tools" ]; then tools=$(cd "$root/../.tools" && pwd); export PATH="$PATH:$tools"; fi
export GIT_CONFIG_NOSYSTEM=1 GIT_PAGER=cat PAGER=cat GIT_EDITOR=true GIT_TERMINAL_PROMPT=0

status=0
"$py" "$root/tests/mdrun.py" "$@" || status=$?
rm -rf "$lab_home"
exit $status
