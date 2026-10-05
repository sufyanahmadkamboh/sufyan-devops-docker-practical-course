<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 069 · Healthchecks in Compose · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Redis's check is `redis-cli ping | grep -q PONG`: it passes only when Redis really answers. Make Redis unusable for
clients without stopping it, by requiring a password (`redis-cli CONFIG SET requirepass x`). Show that the container
turns `unhealthy`, then undo the change and show it turns `healthy` again.

## Solution

```bash
cd ~/docker-practice/lesson-069
docker compose exec redis redis-cli CONFIG SET requirepass x > /dev/null
docker compose exec redis redis-cli ping
sleep 25
echo "after 25 s: $(docker inspect lesson-069-redis-1 --format '{{.State.Health.Status}}')"
docker compose exec redis redis-cli -a x --no-auth-warning CONFIG SET requirepass "" > /dev/null
sleep 3
echo "after the undo: $(docker inspect lesson-069-redis-1 --format '{{.State.Health.Status}}') again"
```

```text
NOAUTH Authentication required.

after 25 s: unhealthy
after the undo: healthy again
```

Without a password, `PING` gets `NOAUTH` instead of `PONG`, so `grep -q PONG` fails and, after 10 failed checks 2 s
apart, the container is `unhealthy`. Whether the plain `redis-cli ping` would have noticed depends on its exit code for
an error reply; matching the expected answer does not depend on such details. A good check fails whenever the service
is unusable.
