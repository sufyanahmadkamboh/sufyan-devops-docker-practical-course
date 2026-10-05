<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 090 · Multi-stage builds for Java · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

`Dockerfile.jlink` uses `jdeps` to find the modules the jar needs and `jlink` to build a runtime with only those,
running on plain `alpine:3.23`. Build it as `java-jlink:1.0`, find out which modules it contains, check that the API
works, and compare its size with `java-multi:1.0`.

## Solution

```bash
cd ~/docker-practice/lesson-090
docker build -q -f Dockerfile.jlink -t java-jlink:1.0 . > /dev/null
docker run --rm --entrypoint /opt/jre/bin/java java-jlink:1.0 --list-modules
docker run -d --name java-jlink -p 8093:8080 java-jlink:1.0 > /dev/null
sleep 2
curl -s http://localhost:8093/health; echo
docker image ls --filter 'reference=java-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```text
java.base@25.0.4.1
jdk.httpserver@25.0.4.1
{"status":"ok"}
java-jlink:1.0	78.9MB
java-multi:broken	305MB
java-multi:fixed	305MB
java-multi:1.0	305MB
java-single:1.0	418MB
```

A runtime with two modules instead of the full JRE. The trade-off: if a later version of the code uses another module
(for example `java.sql`), the image must be rebuilt with it, which `jdeps` in the Dockerfile does automatically.
