<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 045 · Comparing the stacks · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find out which Linux distribution each image is based on, by reading `/etc/os-release` in each one.

**Expected result.** Python's image is Debian (`-slim`), the other four are Alpine.

**Verification.**

```bash
for app in node-api python-api go-api java-api php-app; do
  echo "$app: $(docker run --rm "stack-$app:1.0" sh -c '. /etc/os-release; echo $PRETTY_NAME')"
done
```
