<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 024 · WORKDIR · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build `Dockerfile.fixed` as `menu:1.0`, run it, then run the same image with `-w /` and the command
`ls app` to see where the file is.

**Expected result.** The menu is printed; `ls app` in `/` lists `menu.csv`.

**Verification.**

```bash
cd ~/docker-practice/lesson-024
docker build -q -f Dockerfile.fixed -t menu:1.0 . > /dev/null
docker run --rm menu:1.0
docker run --rm -w / menu:1.0 ls app
```
