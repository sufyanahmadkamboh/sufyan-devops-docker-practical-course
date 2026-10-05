<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 014 · Container logs · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

A container crashes on start. Without running anything inside it, find out why from its log, and show the exit code.

```bash
docker run -d --name crasher alpine:3.23 sh -c 'echo "loading config /etc/app/config.yml"; cat /etc/app/config.yml'
```

## Solution

```bash
sleep 1
docker logs crasher
docker inspect --format 'exit code {{.State.ExitCode}}' crasher
```

```text
loading config /etc/app/config.yml
cat: can't open '/etc/app/config.yml': No such file or directory
exit code 1
```

The log shows the last thing the program did and its error: the configuration file is missing. Logs survive the crash
because the container still exists; with `--rm` they would be gone with it (troubleshooting problem 01).
