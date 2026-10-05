<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 065 · Networking in Compose · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Without editing `compose.yaml`, prove that `tools` can reach the API but not Redis: from `tools`, call the API's
`/health` endpoint on port 5000, then try Redis's port 6379.

## Solution

```bash
cd ~/docker-practice/lesson-065
docker compose exec tools wget -qO- http://api:5000/health; echo
docker compose exec tools nc -z -w 2 redis 6379 2>&1 || echo "redis unreachable"
```

```text
{"status":"ok"}

nc: bad address 'redis'
redis unreachable
```

Inside the network, services talk on their **container** ports (5000), not on the published host ports (8080). The
`frontend` network has no way to Redis: separating networks limits what a compromised front-end container can reach.
