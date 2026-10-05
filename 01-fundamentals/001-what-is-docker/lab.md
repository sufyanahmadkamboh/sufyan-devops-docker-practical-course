<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 001 · What is Docker? · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run the PHP 8.5 command-line interpreter from the `php:8.5-fpm-alpine` image and print its version,
without installing PHP.

**Expected result.** A line starting with `PHP 8.5`.

**Verification.**

```bash
docker run --rm php:8.5-fpm-alpine php --version
```
