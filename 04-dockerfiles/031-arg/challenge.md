<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 031 · ARG · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

A build step needs a token to download a private package. Show the leak with `ARG` (use the fake value
`example-token-123`), then pass the token with a **build secret** instead (`RUN --mount=type=secret,…` and
`docker build --secret`), and prove it is not in the history.

The solution is in [solution.md](solution.md).
