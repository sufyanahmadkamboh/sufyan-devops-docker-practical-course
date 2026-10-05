<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 026 · RUN · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

`/bin/sh -c` only reports the exit status of the **last** command of a pipeline. Show that this step passes although
its first command fails, then make it fail correctly:

```text
RUN false | echo "pipeline finished"
```

## Solution

```bash
cd ~/docker-practice/lesson-026
printf 'FROM alpine:3.23\nRUN false | echo "pipeline finished"\n' > Dockerfile.pipe
docker build -q -f Dockerfile.pipe -t run-demo:pipe . > /dev/null && echo "hidden failure: built"
printf 'FROM alpine:3.23\nRUN set -o pipefail && false | echo "pipeline finished"\n' > Dockerfile.pipefail
docker build -q -f Dockerfile.pipefail -t run-demo:pipefail . > /dev/null 2>&1 || echo "pipefail: build failed"
```

```text
hidden failure: built
pipefail: build failed
```

`set -o pipefail` makes a pipeline fail when any part of it fails. It matters for steps like
`RUN wget -O- https://… | tar -xz`: without it, a failed download can still produce a "successful" layer.
