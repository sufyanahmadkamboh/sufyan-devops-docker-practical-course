<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 069 · Healthchecks in Compose · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Redis's check is `redis-cli ping | grep -q PONG`: it passes only when Redis really answers. Make Redis unusable for
clients without stopping it, by requiring a password (`redis-cli CONFIG SET requirepass x`). Show that the container
turns `unhealthy`, then undo the change and show it turns `healthy` again.

The solution is in [solution.md](solution.md).
