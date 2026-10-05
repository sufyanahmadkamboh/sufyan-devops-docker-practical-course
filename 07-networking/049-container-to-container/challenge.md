<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 049 · Container-to-container communication · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Keep `REDIS_HOST=cache` but make it work **without** renaming anything: give the `redis` container the additional
DNS name `cache` on `cafe-net` (a network alias), then start an API with `REDIS_HOST=cache` on port 8082.

The solution is in [solution.md](solution.md).
