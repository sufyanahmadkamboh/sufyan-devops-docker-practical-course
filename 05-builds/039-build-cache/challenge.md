<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 039 · The build cache · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

The cache key includes the files' **content**, not their timestamps. Prove it: `touch app.py` (new modification time,
same content) and rebuild `cache-api:4`. Is `COPY . .` cached?

The solution is in [solution.md](solution.md).
