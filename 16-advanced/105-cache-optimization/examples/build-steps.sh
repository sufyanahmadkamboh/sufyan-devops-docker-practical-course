#!/bin/sh
# build-steps.sh DOCKER-BUILD-ARGS...: run docker build and print, for every Dockerfile step, whether it was
# taken from the cache or executed. Example: sh build-steps.sh -f Dockerfile.after -t cafe-api:after .
# (FROM is shown as "base": the base image is never rebuilt, only looked up.)
docker build --progress plain "$@" 2>&1 | awk '
  /^#[0-9]+ \[[^]]*[0-9]+\/[0-9]+\]/ {
    id = $1
    if (!(id in step)) { order[++n] = id; sub(/^#[0-9]+ /, ""); sub(/^\[stage-0 /, "["); step[id] = $0 }
    next
  }
  /^#[0-9]+ CACHED/ { cached[$1] = 1 }
  /^ERROR|^#[0-9]+ ERROR/ { print; failed = 1 }
  END {
    for (i = 1; i <= n; i++) {
      s = step[order[i]]
      state = (s ~ /^\[[0-9]+\/[0-9]+\] FROM /) ? "base" : (order[i] in cached ? "cached" : "ran")
      match(s, /^\[[0-9]+/)
      num = substr(s, 2, RLENGTH - 1) + 0
      line[num] = sprintf("%-6s %s", state, substr(s, 1, 70))
      if (num > last) last = num
    }
    for (i = 1; i <= last; i++) if (i in line) print line[i]
    exit failed
  }
'
