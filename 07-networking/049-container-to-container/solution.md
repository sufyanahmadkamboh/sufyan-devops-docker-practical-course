<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 049 · Container-to-container communication · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Keep `REDIS_HOST=cache` but make it work **without** renaming anything: give the `redis` container the additional
DNS name `cache` on `cafe-net` (a network alias), then start an API with `REDIS_HOST=cache` on port 8082.

## Solution

```bash
docker network disconnect cafe-net redis
docker network connect --alias cache cafe-net redis
docker run -d --name api3 --network cafe-net -e REDIS_HOST=cache -p 8082:5000 cafe-api:1.0 > /dev/null
sleep 2
curl -s http://localhost:8082/visits
```

```text
{"visits":5}
```

An alias is an extra DNS name on one network. Compose uses the service name as an alias in the same way (lesson 065).
