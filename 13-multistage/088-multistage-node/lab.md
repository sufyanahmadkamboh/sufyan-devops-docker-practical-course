<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 088 · Multi-stage builds for Node.js · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Count the packages in `node_modules` of the build stage and of the final image. Build the stage with
`--target build`.

**Expected result.** The build stage has the TypeScript packages; the final image has an empty (or no) `node_modules`,
because this API has no production dependencies.

**Verification.**

```bash
docker build -q --target build -t ts-multi:build . > /dev/null
echo "build: $(docker run --rm ts-multi:build sh -c 'ls node_modules | wc -l') packages"
echo "final: $(docker run --rm ts-multi:1.0 sh -c 'ls node_modules 2>/dev/null | wc -l') packages"
```
