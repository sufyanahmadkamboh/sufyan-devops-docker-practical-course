<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 043 · Containerizing a Java application · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-043 examples/java-api
cp 06-application-containerization/043-containerize-java/examples/Dockerfile* ~/docker-practice/lesson-043/
cd ~/docker-practice/lesson-043
ls . src
```

## Demonstration

```bash
docker build -q -t java-api:1.0 . > /dev/null
docker image ls java-api
docker run -d --name java-api -p 8087:8080 java-api:1.0 > /dev/null
```

```bash
curl -s http://localhost:8087/
```

```bash
docker run --rm -m 512m java-api:1.0 java -XX:+PrintFlagsFinal -version 2>/dev/null | grep -w MaxHeapSize
```

```bash
cat Dockerfile.spring-boot
```

## Hands-on lab

```bash
docker run --rm -m 512m -e JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75 java-api:1.0 \
  java -XX:+PrintFlagsFinal -version 2>&1 | grep -E 'Picked up|MaxHeapSize '
```

## Break it

```bash
docker run --rm java-api:1.0 java -cp app.jar main 2>&1
```

## Troubleshoot it

```bash
docker run --rm java-api:1.0 sh -c 'jar --list --file app.jar; unzip -p app.jar META-INF/MANIFEST.MF'
```

## Fix it

```bash
docker run --rm -d --name java-fixed java-api:1.0 java -cp app.jar Main > /dev/null
sleep 2
docker logs java-fixed
docker rm -f java-fixed > /dev/null
```

## Practice challenge

```bash
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' eclipse-temurin
docker run --rm eclipse-temurin:25-jre-alpine javac -version 2>&1 || true
```

## Cleanup

```bash
docker rm -f java-api > /dev/null
docker image rm -f java-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-043
```
