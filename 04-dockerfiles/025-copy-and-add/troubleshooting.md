<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 025 · COPY and ADD · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The service also needs the shared configuration file, which lives in the folder next to it:

```bash
printf 'FROM alpine:3.23\nWORKDIR /app\nCOPY menu.csv .\nCOPY ../shared/config.json .\n' > Dockerfile.config
docker build -f Dockerfile.config -t copy-demo:config . 2>&1 | grep -E '>>>|ERROR'
```

```text
#7 ERROR: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::npbjpnozw376q5hsmeeslrqen: "/shared/config.json": not found
   4 | >>> COPY ../shared/config.json .
ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::npbjpnozw376q5hsmeeslrqen: "/shared/config.json": not found
```

## Troubleshoot it

`"/shared/config.json": not found`, although the file exists on your disk. Look at the path in the message: the `..`
is gone. Paths in `COPY` are always **inside** the build context, so `../shared` is cut back to `/shared` within
`menu-service/`, where there is no such folder. Docker sends only the build context to the builder; it cannot read
anything else from your computer (this is a security feature: a Dockerfile from a repository cannot copy your files
from elsewhere). Check what the context contains:

```bash
ls -R .
```

## Fix it

Make the context the folder that contains everything the build needs, and point to the Dockerfile with `-f`:

```bash
cd ~/docker-practice/lesson-025
printf 'FROM alpine:3.23\nWORKDIR /app\nCOPY menu-service/menu.csv .\nCOPY shared/config.json .\nCMD ["cat", "config.json"]\n' > menu-service/Dockerfile.config
docker build -q -f menu-service/Dockerfile.config -t copy-demo:config . > /dev/null
docker run --rm copy-demo:config
```

```text
{
  "currency": "EUR",
  "opening_hours": "07:00-18:00"
}
```

The context is now `lesson-025/` (the `.`), so both folders are inside it, and the `COPY` paths are relative to it.
The other way is to copy the file into `menu-service/` before building. A large context is slow to send, which
`.dockerignore` solves (lesson 037).
