<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 039 · The build cache · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The cache key includes the files' **content**, not their timestamps. Prove it: `touch app.py` (new modification time,
same content) and rebuild `cache-api:4`. Is `COPY . .` cached?

## Solution

```bash
cd ~/docker-practice/lesson-039
touch app.py
docker build -t cache-api:4 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'COPY \. \.'
```

```text
#9 [5/5] COPY . .
#9 CACHED
```

Cached: BuildKit checksums the files' content and metadata it cares about, not the modification time. A `git checkout`
of the same commit on a CI machine therefore reuses the cache, as long as the cache is available there (lesson 105).
