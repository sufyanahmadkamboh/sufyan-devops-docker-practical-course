<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 044 · Containerizing a PHP application · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Look at the processes in the PHP container. Which user runs the FPM **master**, and which user runs
the **workers** that execute your code?

**Expected result.** `php-fpm: master process` runs as `root`, the `php-fpm: pool www` workers as `www-data`.

**Verification.**

```bash
docker exec php ps -o user,args
```
