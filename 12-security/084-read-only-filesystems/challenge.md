<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 084 · Read-only file systems · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Run the Python built-in web server (`python -m http.server 8081`) from `python:3.14-alpine` with a read-only root
file system, serving files from a tmpfs at `/srv`. Write a file into `/srv` with `docker exec`, then fetch it with
`curl`.

The solution is in [solution.md](solution.md).
