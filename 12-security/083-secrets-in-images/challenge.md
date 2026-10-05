<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 083 · Secrets in images · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

The application needs `DB_PASSWORD` at run time. Remove it from the image entirely and provide it when the container
starts, from a file, so the password is not in the image and not in your shell history. Prove that the image has no
`DB_PASSWORD`, but the container does.

The solution is in [solution.md](solution.md).
