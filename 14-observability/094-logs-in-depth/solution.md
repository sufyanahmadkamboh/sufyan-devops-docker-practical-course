<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 094 · Logs in depth · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Using only `docker logs` and shell redirection, count how many orders the worker has reported as **failed** so far,
and print the last failure with its Docker timestamp.

## Solution

```bash
echo "failed orders: $(docker logs worker 2>&1 >/dev/null | wc -l)"
docker logs -t worker 2>&1 >/dev/null | tail -1
```

```text
failed orders: 1
2026-10-05T16:59:49.006353363Z ERROR order 5: payment declined
```

`2>&1 >/dev/null` sends the container's stderr into the pipe and discards its stdout (the order of the redirections
matters). Because the worker writes errors to stderr, no `grep` is needed.
