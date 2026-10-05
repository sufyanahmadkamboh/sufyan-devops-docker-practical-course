<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 090 · Multi-stage builds for Java · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-090 examples/java-api
cp 13-multistage/090-multistage-java/examples/Dockerfile* ~/docker-practice/lesson-090/
cd ~/docker-practice/lesson-090
cat Dockerfile
```

## Demonstration

```bash
docker build -q -f Dockerfile.single -t java-single:1.0 . > /dev/null
docker build -q -t java-multi:1.0 . > /dev/null
docker image ls --filter 'reference=java-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```bash
docker run -d --name java-multi -p 8092:8080 java-multi:1.0 > /dev/null
docker ps --filter name=java-multi --format '{{.Names}}: {{.Status}}'
```

```bash
curl -s http://localhost:8092/
```

```bash
docker run --rm --entrypoint sh java-multi:1.0 -c 'java -version 2>&1 | head -1; javac -version 2>&1 || true'
```

## Hands-on lab

```bash
docker exec java-multi id
docker run --rm -m 512m --entrypoint java java-multi:1.0 -XX:MaxRAMPercentage=75 -XX:+PrintFlagsFinal -version 2>/dev/null | grep -w MaxHeapSize
```

## Break it

```bash
docker build -q -f Dockerfile.broken -t java-multi:broken . > /dev/null
docker image ls --filter 'reference=java-multi' --format '{{.Repository}}:{{.Tag}}'
```

```bash
docker run --rm java-multi:broken 2>&1
```

## Troubleshoot it

```bash
docker run --rm --entrypoint sh java-multi:broken -c 'echo "working directory: $(pwd)"; find / -name app.jar 2>/dev/null; true'
diff Dockerfile.broken Dockerfile || true
```

## Fix it

```bash
docker build -q -t java-multi:fixed . > /dev/null
docker run -d --name java-fixed java-multi:fixed > /dev/null
sleep 2
docker logs java-fixed
docker rm -f java-fixed > /dev/null
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-090
docker build -q -f Dockerfile.jlink -t java-jlink:1.0 . > /dev/null
docker run --rm --entrypoint /opt/jre/bin/java java-jlink:1.0 --list-modules
docker run -d --name java-jlink -p 8093:8080 java-jlink:1.0 > /dev/null
sleep 2
curl -s http://localhost:8093/health; echo
docker image ls --filter 'reference=java-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

## Cleanup

```bash
docker rm -f java-multi java-jlink java-fixed > /dev/null 2>&1 || true
docker image rm -f java-single:1.0 java-multi:1.0 java-multi:broken java-multi:fixed java-jlink:1.0 > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-090
```
