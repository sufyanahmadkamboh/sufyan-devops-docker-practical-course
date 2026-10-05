<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 088 · Multi-stage builds for Node.js · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The build stage is useful during development too: build only it, then run the TypeScript compiler's type check
(`npx tsc --noEmit`) inside it, without creating a final image.

## Solution

```bash
cd ~/docker-practice/lesson-088
docker build -q --target build -t ts-multi:build . > /dev/null
docker run --rm ts-multi:build sh -c 'npx tsc --noEmit && echo "types ok"'
```

```text
types ok
```

The final image could not do this: it has no TypeScript. CI pipelines run checks like this against the build stage
(`--target build`) and ship the final stage.
