<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 061 · Configuration vs secrets · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

The application needs an API token. Mount it as a secret file into a container and read it from the file in the
container's command, so that neither `docker inspect` nor the command line contains the token.

The solution is in [solution.md](solution.md).
