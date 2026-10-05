<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 089 · Multi-stage builds for Go · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Without a shell in the image, how do you debug the running `go-distroless` container's network? Start a throw-away
`busybox:1.37` container that **shares its network namespace** (`--network container:NAME`) and call the API's
`/health` endpoint on `localhost` from there.

The solution is in [solution.md](solution.md).
