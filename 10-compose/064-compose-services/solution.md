<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 064 · Services · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Both replicas share the same Redis. Call `/visits` on port 8080 and on port 8081, and show that the counter is shared
while `/` reports two different container hostnames.

## Solution

```bash
cd ~/docker-practice/lesson-064
curl -s localhost:8080/visits
curl -s localhost:8081/visits
curl -s localhost:8080/ | grep -o '"hostname":"[0-9a-f]*"'
curl -s localhost:8081/ | grep -o '"hostname":"[0-9a-f]*"'
```

```text
{"visits":2}
{"visits":3}
"hostname":"7b94b3ccb608"
"hostname":"ac259f414814"
```

The state lives in Redis, not in the API containers: that is what makes the API safe to scale (stateless services).
