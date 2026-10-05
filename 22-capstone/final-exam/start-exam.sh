#!/usr/bin/env bash
# start-exam.sh: prepare the final exam: a folder ~/docker-practice/exam and a set of containers, some of them broken.
# Running it again resets the exam. Run it from the course folder:  bash 22-capstone/final-exam/start-exam.sh
set -euo pipefail

course=$(cd "$(dirname "$0")/../.." && pwd)
exam="$HOME/docker-practice/exam"

# a clean start: remove what an earlier attempt left behind
docker rm -f exam-web exam-worker exam-api exam-cache exam-client exam-notes exam-greeter exam-registry > /dev/null 2>&1 || true
(cd "$exam/compose" 2> /dev/null && docker compose -p exam down -v > /dev/null 2>&1) || true
docker network rm exam-front exam-back > /dev/null 2>&1 || true
docker volume rm exam-notes-data > /dev/null 2>&1 || true
rm -rf "$exam"

mkdir -p "$exam"
cp -r "$course/22-capstone/final-exam/files/." "$exam/"
cp "$course/22-capstone/final-exam/check-exam.sh" "$exam/"   # grade from anywhere: bash ~/docker-practice/exam/check-exam.sh
cp "$course/examples/go-api/main.go" "$course/examples/go-api/go.mod" "$exam/optimize/"
cp "$course/examples/python-api/app.py" "$course/examples/python-api/requirements.txt" "$exam/compose/"
printf '# one answer per line, key=value (tasks 1-4 and 6)\n' > "$exam/answers.txt"

docker network create exam-front > /dev/null
docker network create exam-back > /dev/null

# tasks 1-2: a running web server to inspect
docker run -d --name exam-web -p 8090:80 nginx:1.30-alpine > /dev/null
# task 3: a container that does not stay up
docker run -d --name exam-worker alpine:3.23 sh -c 'echo "worker starting"; pyhton /app/worker.py' > /dev/null
# task 4: a container that reports its problem only in its logs
docker run -d --name exam-api alpine:3.23 sh -c 'echo "boot ok"; echo "ERROR: cannot open /data/orders.db: permission denied" >&2; exec sleep 3600' > /dev/null
# tasks 5-6: a client and a cache that cannot reach each other
docker run -d --name exam-cache --network exam-back redis:8-alpine > /dev/null
docker run -d --name exam-client --network exam-front alpine:3.23 sleep 3600 > /dev/null
# task 7: notes written into the container's writable layer
docker run -d --name exam-notes alpine:3.23 sh -c 'mkdir -p /data && echo "remember the milk" > /data/note.txt && exec sleep 3600' > /dev/null
# task 8: a service that needs configuration
docker build -q -t exam-greeter:1.0 "$exam/greeter" > /dev/null
docker run -d --name exam-greeter exam-greeter:1.0 > /dev/null

echo "exam ready: ~/docker-practice/exam (13 tasks: 22-capstone/final-exam/README.md)"
