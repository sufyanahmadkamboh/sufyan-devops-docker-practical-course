# Lesson 091 · Measuring image size

> Level 14 · Multi-stage builds · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

"Make the image smaller" only means something if you measure. Docker reports two sizes for an image: the **disk
usage** (the unpacked files on the engine's disk) and the **content size** (the compressed layers a registry stores
and a `docker pull` downloads). `docker history` breaks the size down by instruction, so you can see which line of the
Dockerfile is responsible. This lesson measures the module's Node.js images and finds an oversized layer.

## Visual

```text
  docker image ls ts-multi                 docker history ts-multi:1.0 (newest first)
  IMAGE          DISK USAGE  CONTENT SIZE    SIZE     CREATED BY
  ts-multi:1.0   …MB         …MB             0B       CMD ["node" "dist/server.js"]
                 │           │               …kB      COPY /app/dist ./dist          ◀ your layers
                 │           │               …kB      RUN npm ci --omit=dev          ◀
                 │           │               …        … node:24-alpine's own layers  ◀ the base image
                 │           └─ compressed: what is pushed and pulled over the network
                 └─ unpacked: what the image occupies on disk

  your share of the image = the layers above the base image's layers
```

## Lab setup

The TypeScript API and Dockerfiles from lesson 088, plus one more variant:

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-091 13-multistage/088-multistage-node/examples/ts-api
cp 13-multistage/088-multistage-node/examples/Dockerfile 13-multistage/088-multistage-node/examples/Dockerfile.single \
   13-multistage/091-measuring-image-size/examples/Dockerfile.copyall ~/docker-practice/lesson-091/
cd ~/docker-practice/lesson-091
ls
```

## Demonstration

Build the single-stage and the multi-stage image, and compare both numbers with the base image:

<!-- test: contains=ts-multi; output -->
```bash
docker build -q -f Dockerfile.single -t ts-single:1.0 . > /dev/null
docker build -q -t ts-multi:1.0 . > /dev/null
docker image ls node:24-alpine
docker image ls ts-single
docker image ls ts-multi
```

```text
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
node:24-alpine   ebfe2f904627        242MB           62MB        
IMAGE           ID             DISK USAGE   CONTENT SIZE   EXTRA
ts-single:1.0   43f445414b5d        289MB         72.5MB        
IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
ts-multi:1.0   ee4c8ea01f71        245MB         62.2MB        
```

The content size (compressed) is roughly a quarter of the disk usage: text files and binaries compress well. Both
numbers include the base image, which is the same for both variants and, on a server that already has it, is not
downloaded again.

What did **our** Dockerfile add? `docker history` lists every layer; the ones created by our instructions come first:

<!-- test: contains=COPY; output -->
```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' ts-multi:1.0 | head -7
```

```text
0B	CMD ["node" "dist/server.js"]
0B	EXPOSE [3000/tcp]
0B	USER node
16.4kB	COPY /app/dist ./dist # buildkit
2.72MB	RUN /bin/sh -c npm ci --omit=dev # buildkit
16.4kB	COPY package.json package-lock.json ./ # bui…
8.19kB	WORKDIR /app
```

A few MB at most (most of it is npm's own files from `npm ci`): almost the whole image is Node.js itself. Programmatically, the exact numbers come from
`docker image inspect`:

<!-- test: contains=bytes; output -->
```bash
docker image inspect --format '{{.Size}} bytes (content), {{len .RootFS.Layers}} layers' ts-multi:1.0
```

```text
62167052 bytes (content), 8 layers
```

## Command breakdown

| Command | What it measures |
|---|---|
| `docker image ls` → DISK USAGE | unpacked size on the engine's disk (shared layers counted in every image) |
| `docker image ls` → CONTENT SIZE | compressed size: what a registry stores and a pull downloads |
| `docker history IMAGE` | size of each layer and the instruction that created it |
| `docker image inspect --format '{{.Size}}'` | the content size in bytes, for scripts |
| `docker system df` | disk used by all images, containers, volumes and the build cache |

## Hands-on lab

**Instructions.** Show how much disk all images, containers, volumes and the build cache use on your engine, and how
much of it is reclaimable.

**Expected result.** A table with the four types, their total size and the `RECLAIMABLE` column. Shared base layers
are counted once here, unlike in `docker image ls`.

**Verification.**

<!-- test: contains=Build Cache -->
```bash
docker system df
```

## Break it

`Dockerfile.copyall` "simplifies" the final stage: instead of installing production dependencies and copying `dist/`,
it copies the whole `/app` folder of the build stage:

<!-- test: contains=ts-copyall; output -->
```bash
grep 'COPY --from' Dockerfile.copyall
docker build -q -f Dockerfile.copyall -t ts-copyall:1.0 . > /dev/null
docker image ls --filter 'reference=ts-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```text
COPY --from=build /app ./
ts-copyall:1.0	274MB
ts-multi:1.0	245MB
ts-single:1.0	289MB
```

It is a multi-stage build, yet the image is almost as big as the single-stage one.

## Troubleshoot it

Find the layer responsible:

<!-- test: contains=COPY /app ./; output -->
```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' ts-copyall:1.0 | head -5
```

```text
0B	CMD ["node" "dist/server.js"]
0B	EXPOSE [3000/tcp]
0B	USER node
27.1MB	COPY /app ./ # buildkit
8.19kB	WORKDIR /app
```

One `COPY` adds tens of MB. What did it bring along?

<!-- test: contains=typescript; output -->
```bash
docker run --rm ts-copyall:1.0 sh -c 'du -sh node_modules/* src dist | sort -h'
```

```text
8.0K	dist
8.0K	src
244.0K	node_modules/undici-types
2.7M	node_modules/@types
22.9M	node_modules/typescript
```

The build stage's `node_modules` (with the TypeScript compiler) and the sources: exactly what multi-stage was
supposed to leave behind. `COPY --from` copies whatever you name; copying a whole directory of the build stage brings
the build tools with it.

## Fix it

Copy only the build **output**, and install production dependencies in the final stage (`Dockerfile`):

<!-- test: contains=ts-multi -->
```bash
diff Dockerfile.copyall Dockerfile || true
docker image ls --filter 'reference=ts-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

## Practice challenge

Write a small size report: for `ts-single:1.0`, `ts-copyall:1.0` and `ts-multi:1.0`, print the content size in MB
(from `docker image inspect`) and how many MB larger than `node:24-alpine` each one is.

<details>
<summary>Solution</summary>

<!-- test: contains=ts-multi:1.0; output -->
```bash
base=$(docker image inspect --format '{{.Size}}' node:24-alpine)
for image in ts-single:1.0 ts-copyall:1.0 ts-multi:1.0; do
  size=$(docker image inspect --format '{{.Size}}' "$image")
  echo "$image  $((size / 1000000)) MB content, +$(((size - base) / 1000000)) MB over the base image"
done
```

```text
ts-single:1.0  72 MB content, +10 MB over the base image
ts-copyall:1.0  66 MB content, +4 MB over the base image
ts-multi:1.0  62 MB content, +0 MB over the base image
```

Integer division rounds down; the point is the comparison. Comparing against the base image isolates what your
Dockerfile adds, which is the part you control. A CI job can fail a build when that number grows unexpectedly.

</details>

## Real-world example

Teams add an image size check to CI: after the build, `docker image inspect --format '{{.Size}}'` is compared with the
previous release, and a jump of more than a few MB fails the pipeline until someone looks at `docker history`. Tools
like `dive` show the same per-layer breakdown interactively, file by file. The usual culprits are a `COPY . .` without
`.dockerignore` (lesson 037), a cleanup in a separate `RUN` (lesson 038) and a `COPY --from` that copies too much (this
lesson).

## Recap

- Disk usage = unpacked size; content size = compressed, what is pulled and pushed.
- `docker history` attributes size to Dockerfile instructions; your layers are above the base image's.
- `docker image inspect --format '{{.Size}}'` gives exact bytes for scripts and CI checks.
- `COPY --from` copies exactly what you name: copy build output, not build folders.

## Cleanup

<!-- test -->
```bash
docker image rm -f ts-single:1.0 ts-multi:1.0 ts-copyall:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-091
```

Next: [Lesson 092 · HEALTHCHECK](../../14-observability/092-healthcheck/README.md)
