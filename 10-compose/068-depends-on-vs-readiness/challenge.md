<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 068 · depends_on vs readiness · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Add an `api` service (image `alpine:3.23`, command `echo "api starting after the migration"`) that starts only after
`migrate` has **finished successfully**. Show the order in which the three services started.

The solution is in [solution.md](solution.md).
