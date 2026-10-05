<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 077 · Image naming · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Remove the tag `localhost:5000/cafe-team/cafe-api:1` locally and show that the image is still there under its other
names. Then show which tag names in the registry are unaffected.

## Solution

```bash
docker image rm localhost:5000/cafe-team/cafe-api:1
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -c "cafe-team/cafe-api"
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```

```text
Untagged: localhost:5000/cafe-team/cafe-api:1
3
{"name":"cafe-team/cafe-api","tags":["1","1.4","1.4.2","sha-3f1a2b4"]}
```

`Untagged`, not `Deleted`: only the name went, the image keeps its other names. The registry is independent of your
local names: its tag `1` is still there.
