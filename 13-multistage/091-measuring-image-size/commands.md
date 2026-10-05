<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 091 · Measuring image size · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-091 13-multistage/088-multistage-node/examples/ts-api
cp 13-multistage/088-multistage-node/examples/Dockerfile 13-multistage/088-multistage-node/examples/Dockerfile.single \
   13-multistage/091-measuring-image-size/examples/Dockerfile.copyall ~/docker-practice/lesson-091/
cd ~/docker-practice/lesson-091
ls
```

## Demonstration

```bash
docker build -q -f Dockerfile.single -t ts-single:1.0 . > /dev/null
docker build -q -t ts-multi:1.0 . > /dev/null
docker image ls node:24-alpine
docker image ls ts-single
docker image ls ts-multi
```

```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' ts-multi:1.0 | head -7
```

```bash
docker image inspect --format '{{.Size}} bytes (content), {{len .RootFS.Layers}} layers' ts-multi:1.0
```

## Hands-on lab

```bash
docker system df
```

## Break it

```bash
grep 'COPY --from' Dockerfile.copyall
docker build -q -f Dockerfile.copyall -t ts-copyall:1.0 . > /dev/null
docker image ls --filter 'reference=ts-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

## Troubleshoot it

```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' ts-copyall:1.0 | head -5
```

```bash
docker run --rm ts-copyall:1.0 sh -c 'du -sh node_modules/* src dist | sort -h'
```

## Fix it

```bash
diff Dockerfile.copyall Dockerfile || true
docker image ls --filter 'reference=ts-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

## Practice challenge

```bash
base=$(docker image inspect --format '{{.Size}}' node:24-alpine)
for image in ts-single:1.0 ts-copyall:1.0 ts-multi:1.0; do
  size=$(docker image inspect --format '{{.Size}}' "$image")
  echo "$image  $((size / 1000000)) MB content, +$(((size - base) / 1000000)) MB over the base image"
done
```

## Cleanup

```bash
docker image rm -f ts-single:1.0 ts-multi:1.0 ts-copyall:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-091
```
