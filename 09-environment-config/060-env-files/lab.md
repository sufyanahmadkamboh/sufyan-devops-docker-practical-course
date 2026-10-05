<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 060 · Environment files · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Write a second file `prod.env` that changes only `GREETING` and `LOG_LEVEL`, and start a container
with **both** files (`app.env` first) to see which values win.

**Expected result.** `APP_VERSION=1.4.0` from `app.env`; `GREETING` and `LOG_LEVEL` from `prod.env`.

**Verification.**

```bash
printf 'GREETING=Welcome, production guest\nLOG_LEVEL=warn\n' > prod.env
docker run --rm --env-file app.env --env-file prod.env alpine:3.23 sh -c 'env | grep -E "GREETING|APP_VERSION|LOG_LEVEL" | sort'
```
