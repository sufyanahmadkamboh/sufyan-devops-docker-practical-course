<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 036 · The build context · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Prove that the builder only ever sees the context: create a file `../secret-note.txt` next to the lab folder, then try
to `COPY` it with `COPY ../../secret-note.txt ./` in a throw-away Dockerfile read from standard input
(`docker build -f - .`). The build must fail.

## Solution

```bash
cd ~/docker-practice/lesson-036/node-api
echo "not for images" > ../../secret-note.txt
printf 'FROM alpine:3.23\nCOPY ../../secret-note.txt ./\n' | docker build -f - -t ctx-api:secret . 2>&1 | grep -o '"/secret-note.txt": not found' | head -1
test "${PIPESTATUS[1]}" -eq 0
```

```text
"/secret-note.txt": not found
```

`-f -` reads the Dockerfile from standard input; the context is still `.`. However many `../` you write, the path is
resolved inside the context: files next to it are out of reach.
