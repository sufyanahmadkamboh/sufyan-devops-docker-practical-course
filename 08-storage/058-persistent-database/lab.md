<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 058 · A persistent database · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find out how much space the database uses in the volume, and which files Postgres created at the top
of its data directory.

**Expected result.** A size of a few tens of megabytes, and entries such as `PG_VERSION`, `base` and `pg_wal`.

**Verification.**

```bash
docker run --rm -v pgdata:/data:ro alpine:3.23 sh -c 'du -sh /data; ls /data/18/docker'
```
