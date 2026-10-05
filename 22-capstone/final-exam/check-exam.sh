#!/usr/bin/env bash
# check-exam.sh: grade the final exam. Every task is checked against the real state of the engine and the files.
#   bash 22-capstone/final-exam/check-exam.sh
set -uo pipefail

exam="$HOME/docker-practice/exam"
answers="$exam/answers.txt"
score=0
answer() { grep -E "^$1=" "$answers" 2> /dev/null | tail -1 | cut -d= -f2- | tr -d '\r' | sed 's/^ *//; s/ *$//'; }
running() { [ "$(docker inspect --format '{{.State.Running}}' "$1" 2> /dev/null)" = true ]; }
task() {   # task NUMBER "DESCRIPTION" COMMAND...
  local n=$1 what=$2
  shift 2
  if "$@" > /dev/null 2>&1; then
    printf 'PASS  task %2s  %s\n' "$n" "$what"
    score=$((score + 1))
  else
    printf 'FAIL  task %2s  %s\n' "$n" "$what"
  fi
}

t1() { [ "$(answer web_image)" = nginx:1.30-alpine ] && [ "$(answer web_port)" = 8090 ]; }
t2() { [ "$(answer redis_entrypoint)" = docker-entrypoint.sh ]; }
t3() { [ "$(answer worker_exit_code)" = 127 ]; }
t4() { [ "$(answer api_error_file)" = /data/orders.db ]; }
t5() { docker inspect --format '{{json .NetworkSettings.Networks}}' exam-client | grep -q '"exam-back"'; }
t6() { [ "$(answer cache_reply)" = +PONG ] && docker exec exam-client sh -c "printf 'PING\r\n' | nc -w 2 exam-cache 6379" | grep -q PONG; }
t7() {
  running exam-notes &&
    docker inspect --format '{{range .Mounts}}{{.Name}}:{{.Destination}} {{end}}' exam-notes | grep -q "exam-notes-data:/data" &&
    docker run --rm -v exam-notes-data:/data alpine:3.23 cat /data/note.txt | grep -q "remember the milk"
}
t8() { running exam-greeter && docker logs exam-greeter 2>&1 | grep -q "greeter started"; }
t9() {
  local size
  size=$(docker image inspect --format '{{.Size}}' exam-optimized:1.0) &&
    [ "$size" -lt 30000000 ] &&
    docker run -d --name exam-check-opt -p 8092:8080 exam-optimized:1.0 &&
    sleep 2 && curl -fsS http://localhost:8092/health | grep -q ok
}
t10() {
  local uid
  uid=$(docker run --rm --entrypoint id exam-nonroot:1.0 -u) && [ "$uid" != 0 ] &&
    docker run -d --name exam-check-nonroot -p 8093:8000 exam-nonroot:1.0 &&
    sleep 2 && curl -fsS http://localhost:8093/ | grep -q exam
}
t11() { curl -fsS http://localhost:8091/visits | grep -q visits; }
t12() {
  local ids
  ids=$(cd "$exam/compose" && docker compose -p exam ps -q) && [ "$(echo "$ids" | wc -l)" -ge 2 ] &&
    for id in $ids; do [ "$(docker inspect --format '{{.State.Health.Status}}' "$id")" = healthy ] || return 1; done
}
t13() { curl -fsS http://localhost:5000/v2/exam/optimized/tags/list | grep -q '"1.0"'; }

docker rm -f exam-check-opt exam-check-nonroot > /dev/null 2>&1 || true
task 1 "inspect a container: image and host port of exam-web" t1
task 2 "inspect an image: the entrypoint of redis:8-alpine" t2
task 3 "why exam-worker exits: its exit code" t3
task 4 "read the logs of exam-api: the file it cannot open" t4
task 5 "networking: exam-client joins the network of exam-cache" t5
task 6 "connectivity: exam-client reaches exam-cache by name" t6
task 7 "volume: exam-notes keeps its data in the volume exam-notes-data" t7
task 8 "environment: exam-greeter runs with GREETING set" t8
task 9 "optimize: exam-optimized:1.0 under 30 MB and working" t9
task 10 "privileges: exam-nonroot:1.0 runs as a non-root user" t10
task 11 "compose: the exam stack answers on localhost:8091/visits" t11
task 12 "health: every service of the exam stack is healthy" t12
task 13 "registry: exam/optimized:1.0 is in the registry on localhost:5000" t13

docker rm -f exam-check-opt exam-check-nonroot > /dev/null 2>&1 || true
echo "score: $score/13"
[ "$score" -eq 13 ]
