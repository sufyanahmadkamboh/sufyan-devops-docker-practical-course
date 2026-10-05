<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 026 · RUN · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A typing error in a package name:

```bash
printf 'FROM alpine:3.23\nRUN apk add --no-cache curll\n' > Dockerfile.broken
docker build --progress=plain -f Dockerfile.broken -t run-demo:broken . 2>&1 | grep -E 'ERROR|curll'
```

```text
#5 [2/2] RUN apk add --no-cache curll
#5 0.630 ERROR: unable to select packages:
#5 0.630   curll (no such package):
#5 0.630     required by: world[curll]
#5 ERROR: process "/bin/sh -c apk add --no-cache curll" did not complete successfully: exit code: 1
 > [2/2] RUN apk add --no-cache curll:
0.630 ERROR: unable to select packages:
0.630   curll (no such package):
0.630     required by: world[curll]
   2 | >>> RUN apk add --no-cache curll
ERROR: failed to build: failed to solve: process "/bin/sh -c apk add --no-cache curll" did not complete successfully: exit code: 1
```

## Troubleshoot it

Two kinds of lines: the step's own output (`#5 0.582 ERROR: unable to select packages: curll (no such package)`), and
Docker's summary (`process "/bin/sh -c apk add --no-cache curll" did not complete successfully: exit code: 1`). Docker
only knows the command exited with 1; the reason is always in the step's output just above, which is why
`--progress=plain` matters when a build fails. Reproduce the step interactively in a container of the base image to
investigate:

```bash
docker run --rm alpine:3.23 sh -c 'apk update -q && apk search curl | grep "^curl-[0-9]"'
```

```text
curl-8.22.0-r0
```

## Fix it

```bash
sed -i.bak 's/curll/curl/' Dockerfile.broken && rm Dockerfile.broken.bak
docker build -q -f Dockerfile.broken -t run-demo:fixed . > /dev/null
docker run --rm run-demo:fixed curl --version | head -1
```
