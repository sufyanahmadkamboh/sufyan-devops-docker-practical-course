<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 086 · Resource limits for security · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Show that the open-file limit works: in a container with `--ulimit nofile=20:20`, open files until the kernel refuses,
and report how many could be opened.

The solution is in [solution.md](solution.md).
