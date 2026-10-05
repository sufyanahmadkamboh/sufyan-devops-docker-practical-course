<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 087 · Why multi-stage builds? · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Stages are also useful for **tests**. Without changing the final image, add a stage `test` (based on `build`) that runs
`go vet ./...`, and build only that stage with `--target test`. Write the new Dockerfile to `Dockerfile.test`.

The solution is in [solution.md](solution.md).
