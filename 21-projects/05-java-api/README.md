# Project 05 · Java API on a JRE

> ⏱ 1 hour · run every command from the course folder

## Goal

Containerize the Java API ([examples/java-api](../../examples/java-api)): compile and package it with the JDK, run it
on the smaller JRE, as a non-root user, with a heap sized from the **container's** memory limit. Measure what the
multi-stage build saves.

## Requirements

- [ ] Build stage `eclipse-temurin:25-jdk-alpine` compiles the code and packages an executable jar
- [ ] Runtime stage `eclipse-temurin:25-jre-alpine` contains only the JRE and the jar, user `app` (10001)
- [ ] `-XX:MaxRAMPercentage=75`: with `--memory 256m` the maximum heap is about 192 MB
- [ ] A healthcheck on `/health`; Docker reports the container **healthy**
- [ ] The JDK and the JRE variants are measured

## Architecture

```text
 eclipse-temurin:25-jdk-alpine                     eclipse-temurin:25-jre-alpine
 ┌──────────────────────────────────┐              ┌───────────────────────────────────┐
 │ javac -d out src/Main.java       │              │ /app/app.jar        user app      │
 │ jar --main-class Main → app.jar  │ ─ app.jar ─▶ │ java -XX:MaxRAMPercentage=75 -jar │
 └──────────────────────────────────┘              │ :8080  /  /health                 │
                                                   └───────────────────────────────────┘
```

Real projects build with Maven or Gradle in the first stage (`mvn -B package`, `./gradlew bootJar` for Spring Boot);
the shape of the Dockerfile is the same.

## Build it

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-05 examples/java-api
cp -r 21-projects/05-java-api/solution/. ~/docker-practice/project-05/
cd ~/docker-practice/project-05
ls -A
```

<!-- test: contains=--main-class Main; output -->
```bash
cat Dockerfile
```

```text
# syntax=docker/dockerfile:1
# Stage 1: compile and package with the full JDK.
FROM eclipse-temurin:25-jdk-alpine AS build
WORKDIR /src
COPY src/ src/
RUN javac -d out src/Main.java \
 && jar --create --file app.jar --main-class Main -C out .

# Stage 2: run the jar on the JRE only (no compiler), as an unprivileged user.
FROM eclipse-temurin:25-jre-alpine
RUN addgroup -S app && adduser -S -G app -u 10001 app
WORKDIR /app
COPY --from=build /src/app.jar .
USER app
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s --retries=3 \
  CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/health"]
# size the heap from the container's memory limit, not from the host's memory
ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]
```

<!-- test: contains=java-api -->
```bash
docker build -q -t java-api:jdk -f Dockerfile.single . > /dev/null
docker build -q -t java-api:1.0 . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' java-api
```

## Verify

<!-- test: contains=java-api:1.0; output -->
```bash
for tag in jdk 1.0; do
  docker image inspect --format "java-api:$tag {{.Size}}" java-api:$tag
done | awk '{ printf "%-14s %6.1f MB\n", $1, $2 / 1000000 }'
```

```text
java-api:jdk    109.9 MB
java-api:1.0     75.5 MB
```

Sizes are content sizes (the compressed layers a pull downloads). The runtime image has no compiler (`javac`), only
what is needed to run the jar:

<!-- test: contains=javac not found; output -->
```bash
docker run --rm --entrypoint sh java-api:1.0 -c 'command -v javac || echo "javac not found"; java -version 2>&1 | head -1'
```

```text
javac not found
openjdk version "25.0.4.1" 2026-08-18 LTS
```

Start it with a memory limit, and check the user, the health and the heap size the JVM chose:

<!-- test: contains=Hello from Java; retry=15 -->
```bash
docker run -d --name java-api -p 8086:8080 --memory 256m java-api:1.0 > /dev/null
curl -s http://localhost:8086/
```

<!-- test: contains=healthy; retry=20 -->
```bash
docker exec java-api id -un
docker inspect --format '{{.State.Health.Status}}' java-api
```

<!-- test: contains=MaxHeapSize; output -->
```bash
docker run --rm --memory 256m --entrypoint java java-api:1.0 -XX:MaxRAMPercentage=75 -XX:+PrintFlagsFinal -version 2>/dev/null | grep -E " MaxHeapSize "
```

```text
   size_t MaxHeapSize                              = 201326592                                 {product} {ergonomic}
```

About 75 % of 256 MiB: the JVM reads the container's limit (cgroups), so the heap fits inside it instead of growing
until the kernel kills the container (lesson 098).

## Break it and fix it

[Dockerfile.broken](solution/Dockerfile.broken) packages the jar without saying which class to start:

<!-- test: fail; contains=no main manifest attribute; output -->
```bash
docker build -q -t java-api:broken -f Dockerfile.broken . > /dev/null
docker run --rm java-api:broken 2>&1
```

```text
no main manifest attribute, in app.jar
```

`java -jar` reads the class to start from the jar's manifest (`META-INF/MANIFEST.MF`, the `Main-Class` line), and
there is none. Look inside the jar:

<!-- test: absent=Main-Class; output -->
```bash
docker run --rm --entrypoint unzip java-api:broken -p /app/app.jar META-INF/MANIFEST.MF
```

```text
Manifest-Version: 1.0
Created-By: 25.0.4.1 (Eclipse Adoptium)
```

The fix is `jar --create --file app.jar --main-class Main …` (Maven and Gradle set it from the build file):

<!-- test: contains=Main-Class: Main -->
```bash
sed -i.bak 's|jar --create --file app.jar -C out .|jar --create --file app.jar --main-class Main -C out .|' Dockerfile.broken
docker build -q -t java-api:broken -f Dockerfile.broken . > /dev/null
docker run --rm --entrypoint unzip java-api:broken -p /app/app.jar META-INF/MANIFEST.MF
```

## Stretch goals

- Build a custom runtime with `jlink --add-modules java.base,jdk.httpserver` in the build stage and copy it onto
  `alpine:3.23`: measure the result.
- Start the container with `--memory 64m` and watch what happens to the JVM (troubleshooting problem 22).
- Add `--read-only --tmpfs /tmp` and check the JVM still starts.

## Cleanup

<!-- test -->
```bash
docker rm -f java-api > /dev/null 2>&1 || true
docker image rm -f java-api:jdk java-api:1.0 java-api:broken > /dev/null
cd ~ && rm -rf ~/docker-practice/project-05
```

Next: [Project 06 · A database container you can back up](../06-database-container/README.md)
