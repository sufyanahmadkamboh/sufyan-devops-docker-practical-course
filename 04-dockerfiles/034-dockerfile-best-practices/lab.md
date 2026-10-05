<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 034 · Dockerfile best practices · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Change one line of `server.js` (the default greeting), then rebuild **both** images with
`--progress=plain` and count how many steps were taken from the cache.

**Expected result.** In the `after` build, the `npm ci` step is `CACHED`; in the `before` build, `npm install` runs
again.

**Verification.**

```bash
cd ~/docker-practice/lesson-034
sed -i.bak 's/Hello from Node.js/Hello from the cafe/' server.js && rm server.js.bak
docker build --progress=plain -f Dockerfile.after -t cafe-api:after . 2>&1 | grep -A1 'RUN npm ci' | grep -q CACHED && echo "after: npm ci CACHED"
docker build --progress=plain -f Dockerfile.before -t cafe-api:before . 2>&1 | grep -A1 'RUN npm install' | grep -q CACHED || echo "before: npm install ran again"
```

The application has no dependencies, so `npm install` is quick here; with a few hundred packages it takes minutes, on
every code change.
