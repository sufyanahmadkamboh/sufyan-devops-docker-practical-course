<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 035 · docker build · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate renamed the Dockerfile to `Dockerfile.prod` for production and now runs the usual command:

```bash
cd ~/docker-practice/lesson-035
mv Dockerfile Dockerfile.prod
docker build -t node-api:prod . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

```text
ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

## Troubleshoot it

`failed to read dockerfile: open Dockerfile: no such file or directory`: the builder looked for the default name,
`Dockerfile`, in the context, and there is none. The build never started. List what is really there:

```bash
ls
```

```text
Dockerfile.prod
package-lock.json
package.json
server.js
```

## Fix it

Name the file explicitly with `-f`:

```bash
docker build -q -f Dockerfile.prod -t node-api:prod . > /dev/null
docker image ls node-api
```

Teams commonly keep several Dockerfiles (`Dockerfile`, `Dockerfile.dev`, `Dockerfile.test`) and choose with `-f`; the
context (`.`) stays the same.
