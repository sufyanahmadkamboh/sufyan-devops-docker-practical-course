<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 040 · Containerizing a Node.js application · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate deletes `package-lock.json` ("it is generated anyway") and rebuilds:

```bash
cd ~/docker-practice/lesson-040
rm package-lock.json
sed -i.bak 's/package.json package-lock.json/package*.json/' Dockerfile && rm Dockerfile.bak
docker build -t node-api:nolock . 2>&1 | grep -E 'npm (error|ERR)' | head -3
test "${PIPESTATUS[0]}" -eq 0
```

```text
#8 0.555 npm error code EUSAGE
#8 0.561 npm error
#8 0.561 npm error The `npm ci` command can only install with an existing package-lock.json or
```

(The `sed` changes the `COPY` to the wildcard `package*.json` so the build gets as far as `npm ci`; with the explicit
`COPY package-lock.json` it would already fail with `not found`.)

## Troubleshoot it

`npm ci` refuses to run without a lockfile, by design: it installs **exactly** what the lockfile records, so that every
build installs the same versions. `npm install` would silently resolve the newest versions allowed by `package.json`,
and two builds of the same commit could contain different code. The lockfile is part of the source code:

```bash
ls package-lock.json 2> /dev/null || echo "no lockfile in the context"
```

## Fix it

Restore the lockfile (in a real project: `git checkout package-lock.json`). If a project really has none, generate it
**once** with Node.js in a container, without installing Node.js locally, and commit it:

```bash
docker run --rm -v "$(pwd):/app" -w /app node:24-alpine npm install --package-lock-only --silent
grep lockfileVersion package-lock.json
```

```bash
docker build -q -t node-api:fixed . > /dev/null
docker image ls node-api
```
