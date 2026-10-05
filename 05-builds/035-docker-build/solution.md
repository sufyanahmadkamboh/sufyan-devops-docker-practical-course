<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 035 · docker build · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Build the API once more as `node-api:quiet`, printing **only** the image ID (nothing else), and check that this ID is
the one `docker image inspect` reports for that tag.

## Solution

```bash
cd ~/docker-practice/lesson-035
id=$(docker build -q -f Dockerfile.prod -t node-api:quiet .)
echo "$id"
[ "$id" = "$(docker image inspect --format '{{.Id}}' node-api:quiet)" ] && echo "same image"
```

`-q` prints the full image ID (`sha256:…`), which scripts use to refer to exactly the image they just built.
