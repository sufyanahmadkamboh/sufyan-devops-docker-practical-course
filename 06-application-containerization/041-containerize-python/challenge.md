<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 041 · Containerizing a Python application · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Gunicorn also reads options from the environment variable `GUNICORN_CMD_ARGS`. Without rebuilding the image, try to
start a container with **4** workers that way (on port 8084) and count the gunicorn processes. Does it work? If not,
find another way that does, still without rebuilding.

The solution is in [solution.md](solution.md).
