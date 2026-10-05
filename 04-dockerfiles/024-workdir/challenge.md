<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 024 · WORKDIR · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Write a Dockerfile that copies `menu.csv` into `/srv/cafe/menu/`, and whose container prints the number of lines of
the file with `wc -l menu.csv` (a relative path), using `WORKDIR` twice: `/srv/cafe`, then `menu`.

The solution is in [solution.md](solution.md).
