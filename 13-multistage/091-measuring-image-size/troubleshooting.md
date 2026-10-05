<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 091 · Measuring image size · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

`Dockerfile.copyall` "simplifies" the final stage: instead of installing production dependencies and copying `dist/`,
it copies the whole `/app` folder of the build stage:

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

```bash
diff Dockerfile.copyall Dockerfile || true
docker image ls --filter 'reference=ts-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```
