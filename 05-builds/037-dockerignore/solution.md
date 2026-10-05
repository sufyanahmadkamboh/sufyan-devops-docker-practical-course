<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 037 · .dockerignore · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write an **allowlist** `.dockerignore`: exclude everything (`*`), then include only `server.js` and `package.json`
with `!` exceptions. Build `ignore-demo:allow` and show that `/app` contains exactly those two files.

## Solution

```bash
cd ~/docker-practice/lesson-037
printf '*\n!server.js\n!package.json\n' > .dockerignore
docker build -q -t ignore-demo:allow . > /dev/null
docker run --rm ignore-demo:allow ls /app
```

```text
package.json
server.js
```

An allowlist is the safest form: a new file (a key someone drops into the folder) is excluded until you deliberately
add it. The trade-off: you must remember to add every new source folder.
