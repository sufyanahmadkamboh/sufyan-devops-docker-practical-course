<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 036 · The build context · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Now the API needs `shared/config.json`. A teammate adds `COPY ../shared/config.json ./config.json` to the Dockerfile
(`Dockerfile.config`) and builds from `node-api/` as usual:

```bash
cd ~/docker-practice/lesson-036/node-api
docker build -f Dockerfile.config -t ctx-api:config . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

```text
#7 ERROR: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::kop341gts9ld444k5tr57om0z: "/shared/config.json": not found
ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::kop341gts9ld444k5tr57om0z: "/shared/config.json": not found
```

## Troubleshoot it

`"/shared/config.json": not found` although the file clearly exists on disk. Look at the path in the message: the
builder turned `../shared/config.json` into `/shared/config.json`, a path at the **root of the context**. A build can
never leave its context: `..` stops at the top of it, for security (a Dockerfile from the internet must not be able to
read `~/.ssh`) and because the context is all the builder received. The file exists, but not in the context:

```bash
ls ../shared/config.json
ls ./shared/config.json 2>&1 || true
```

## Fix it

Make the context the folder that contains **both** directories, and write the `COPY` paths relative to it.
`Dockerfile.fixed` does exactly that:

```bash
cd ~/docker-practice/lesson-036
grep COPY node-api/Dockerfile.fixed
```

```text
COPY node-api/package.json node-api/server.js ./
COPY shared/config.json ./config.json
```

```bash
docker build -q -f node-api/Dockerfile.fixed -t ctx-api:config . > /dev/null
docker run --rm ctx-api:config cat /app/config.json
```

```text
{
  "feature_flags": { "new_menu": true }
}
```

The other option is to copy the file into `node-api/` before building (CI pipelines often assemble a context folder).
What never works is reaching outside the context.
