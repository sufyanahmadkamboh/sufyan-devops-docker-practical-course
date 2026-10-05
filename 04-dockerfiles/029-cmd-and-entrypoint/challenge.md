<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 029 · CMD and ENTRYPOINT together · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Write the entrypoint-script pattern used by official images: a `docker-entrypoint.sh` that prints
`preparing the cafe…` and then runs whatever command it receives with `exec "$@"`, with `CMD ["price", "espresso"]` as
the default. Verify that the default works and that `docker run IMAGE price "flat white"` works too.

The solution is in [solution.md](solution.md).
