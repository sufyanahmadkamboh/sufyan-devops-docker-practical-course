<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 036 · The build context · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** From inside `node-api/`, build with the **parent** folder (`..`) as the context and
`Dockerfile` from the current folder (`-f Dockerfile`). Why does it fail?

**Expected result.** The build fails on `COPY package.json server.js`: these paths are relative to the context
(`..`), where the files are at `node-api/package.json` and `node-api/server.js`.

**Verification.**

```bash
cd ~/docker-practice/lesson-036/node-api
docker build -f Dockerfile -t ctx-api:parent .. 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```
