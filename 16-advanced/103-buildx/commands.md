<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 103 · BuildKit and buildx · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-103 examples/go-api
cp 16-advanced/103-buildx/examples/Dockerfile ~/docker-practice/lesson-103/
cd ~/docker-practice/lesson-103
grep -n "^FROM" Dockerfile
```

## Demonstration

```bash
docker buildx version | cut -d' ' -f1,2
docker buildx ls --format '{{.Name}} {{.DriverEndpoint}}' 2>/dev/null || docker buildx ls
```

```bash
docker buildx build --progress plain -t cafe-go:1.0 --load . 2>&1 | grep -E '^#[0-9]+ \[' | head -8
docker image ls cafe-go --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker buildx build -q --target export --output type=local,dest=out . > /dev/null
ls out
head -c 4 out/go-api | od -c | head -1
```

## Hands-on lab

```bash
docker buildx du | tail -1
docker buildx build -q --target build -t cafe-go:build-stage --load . > /dev/null
for image in cafe-go:build-stage cafe-go:1.0; do
  echo "$image $(docker image inspect --format '{{.Size}}' "$image" | awk '{printf "%.1f MB", $1/1000000}')"
done
```

## Break it

```bash
docker buildx build --target biuld -t cafe-go:build-stage . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
grep -n ' AS ' Dockerfile
```

## Fix it

```bash
docker buildx build -q --target build -t cafe-go:build-stage --load . > /dev/null
docker image ls cafe-go --format '{{.Repository}}:{{.Tag}}'
```

## Practice challenge

```bash
docker buildx build -q --output type=tar,dest=image.tar . > /dev/null
tar -tf image.tar | grep -v '/$' | wc -l
tar -tf image.tar | grep -E 'go-api|passwd'
```

## Cleanup

```bash
docker image rm -f cafe-go:1.0 cafe-go:build-stage > /dev/null 2>&1 || true
cd ~ && rm -rf ~/docker-practice/lesson-103
```
