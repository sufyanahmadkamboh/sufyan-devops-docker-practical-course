<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 036 · The build context · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Prove that the builder only ever sees the context: create a file `../secret-note.txt` next to the lab folder, then try
to `COPY` it with `COPY ../../secret-note.txt ./` in a throw-away Dockerfile read from standard input
(`docker build -f - .`). The build must fail.

The solution is in [solution.md](solution.md).
