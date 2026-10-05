<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 071 · Logs · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show only the lines of the `worker` service that mention an even job number, with timestamps, from the main project.

## Solution

```bash
cd ~/docker-practice/lesson-071
docker compose logs -t --no-log-prefix worker | grep -E "job [0-9]*[02468] done"
```

```text
...
2026-10-05T17:14:50.809757312Z worker: job 8 done
2026-10-05T17:14:54.812446960Z worker: job 10 done
```

`--no-log-prefix` keeps the lines clean for `grep`; `-t` adds Docker's timestamp, even when the application prints none.
