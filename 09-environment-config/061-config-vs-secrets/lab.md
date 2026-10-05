<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 061 · Configuration vs secrets · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show who can read the secret file inside `db-file`, and that the container cannot change it.

**Expected result.** The file is listed under `/run/secrets`; writing to it fails with `Read-only file system`.

**Verification.**

```bash
docker exec db-file ls -l /run/secrets/
docker exec db-file sh -c 'echo changed > /run/secrets/db_password' 2>&1 || true
```
