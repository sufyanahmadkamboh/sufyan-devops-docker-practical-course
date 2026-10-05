<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 046 · Networking fundamentals · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Start two containers on the default network and show that each one has its **own** IP address, but both use the same
gateway.

## Solution

```bash
docker run -d --name one alpine:3.23 sleep 60 > /dev/null
docker run -d --name two alpine:3.23 sleep 60 > /dev/null
for c in one two; do
  echo "$c: $(docker inspect $c --format '{{.NetworkSettings.Networks.bridge.IPAddress}} via {{.NetworkSettings.Networks.bridge.Gateway}}')"
done
docker rm -f one two > /dev/null
```

```text
one: 172.17.0.2 via 172.17.0.1
two: 172.17.0.3 via 172.17.0.1
```

Each container has its own network namespace and address; the bridge's gateway is shared.
