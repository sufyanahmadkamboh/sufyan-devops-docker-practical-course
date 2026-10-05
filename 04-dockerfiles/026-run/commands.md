<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 026 · RUN · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-026
cd ~/docker-practice/lesson-026
```

## Demonstration

```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
RUN apk add --no-cache curl \
 && curl --version | head -1
CMD ["curl", "--version"]
EOF
docker build --progress=plain -t run-demo . 2>&1 | grep -E 'RUN|curl 8'
docker run --rm run-demo | head -1
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-026
printf 'FROM alpine:3.23\nRUN apk add --no-cache curl jq\n' > Dockerfile.tools
docker build -q -f Dockerfile.tools -t run-demo:tools . > /dev/null
docker run --rm run-demo:tools jq --version
```

## Break it

```bash
printf 'FROM alpine:3.23\nRUN apk add --no-cache curll\n' > Dockerfile.broken
docker build --progress=plain -f Dockerfile.broken -t run-demo:broken . 2>&1 | grep -E 'ERROR|curll'
```

## Troubleshoot it

```bash
docker run --rm alpine:3.23 sh -c 'apk update -q && apk search curl | grep "^curl-[0-9]"'
```

## Fix it

```bash
sed -i.bak 's/curll/curl/' Dockerfile.broken && rm Dockerfile.broken.bak
docker build -q -f Dockerfile.broken -t run-demo:fixed . > /dev/null
docker run --rm run-demo:fixed curl --version | head -1
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-026
printf 'FROM alpine:3.23\nRUN false | echo "pipeline finished"\n' > Dockerfile.pipe
docker build -q -f Dockerfile.pipe -t run-demo:pipe . > /dev/null && echo "hidden failure: built"
printf 'FROM alpine:3.23\nRUN set -o pipefail && false | echo "pipeline finished"\n' > Dockerfile.pipefail
docker build -q -f Dockerfile.pipefail -t run-demo:pipefail . > /dev/null 2>&1 || echo "pipefail: build failed"
```

## Cleanup

```bash
docker image rm -f run-demo run-demo:tools run-demo:fixed run-demo:pipe > /dev/null
rm -rf ~/docker-practice/lesson-026
```
