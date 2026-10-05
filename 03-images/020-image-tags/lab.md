<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 020 · Image tags · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build version `1.4.4` with **all three** tags in one `docker build` (repeat `-t`), and check that the
three names point to one ID.

**Expected result.** `cafe-menu:1.4.4`, `cafe-menu:1.4` and `cafe-menu:1` share one image ID.

**Verification.**

```bash
cd ~/docker-practice/lesson-020
docker build -q --build-arg VERSION=1.4.4 -t cafe-menu:1.4.4 -t cafe-menu:1.4 -t cafe-menu:1 . > /dev/null
[ "$(docker image ls -q cafe-menu:1.4.4)" = "$(docker image ls -q cafe-menu:1)" ] && echo "one ID for 1.4.4, 1.4 and 1"
```
