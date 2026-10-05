# Lesson 090 · Multi-stage builds for Java

> Level 14 · Multi-stage builds · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

Java needs the **JDK** (compiler, `jar`, Maven or Gradle) to build and only the **JRE** (the JVM and the class
libraries) to run. A two-stage Dockerfile compiles in `eclipse-temurin:25-jdk-alpine` and runs in
`eclipse-temurin:25-jre-alpine`, copying just the jar. One step further, `jlink` builds a **custom runtime** containing
only the Java modules the application uses.

## Visual

```text
  stage "build"  eclipse-temurin:25-jdk-alpine             final  eclipse-temurin:25-jre-alpine
  ┌────────────────────────────────────────────┐           ┌──────────────────────────────────────┐
  │ javac, jar, jdeps, jlink (JDK tools)       │           │ JVM + full class library (JRE)       │
  │ src/Main.java  →  classes/  →  app.jar     │──COPY────▶│ /app/app.jar                         │
  └────────────────────────────────────────────┘  app.jar  │ USER app                             │
                                                           └──────────────────────────────────────┘
  challenge:  jdeps → "java.base,jdk.httpserver" → jlink → /jre (only those modules) on alpine:3.23
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-090 examples/java-api
cp 13-multistage/090-multistage-java/examples/Dockerfile* ~/docker-practice/lesson-090/
cd ~/docker-practice/lesson-090
cat Dockerfile
```

## Demonstration

Build the single-stage image of lesson 043 (`Dockerfile.single`) for comparison, and the multi-stage one:

<!-- test: contains=java-multi; output -->
```bash
docker build -q -f Dockerfile.single -t java-single:1.0 . > /dev/null
docker build -q -t java-multi:1.0 . > /dev/null
docker image ls --filter 'reference=java-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```text
java-multi:1.0	305MB
java-single:1.0	418MB
```

<!-- test: contains=Up -->
```bash
docker run -d --name java-multi -p 8092:8080 java-multi:1.0 > /dev/null
docker ps --filter name=java-multi --format '{{.Names}}: {{.Status}}'
```

<!-- test: retry=15; contains=Hello from Java; output -->
```bash
curl -s http://localhost:8092/
```

```text
{"message":"Hello from Java","hostname":"02966f82d081"}
```

The final image can run Java but has no compiler:

<!-- test: contains=javac: not found; output -->
```bash
docker run --rm --entrypoint sh java-multi:1.0 -c 'java -version 2>&1 | head -1; javac -version 2>&1 || true'
```

```text
openjdk version "25.0.4.1" 2026-08-18 LTS
sh: javac: not found
```

`--entrypoint sh` replaces the image's `ENTRYPOINT` (which starts the application) for this one container.

## Command breakdown

| Instruction / tool | Meaning |
|---|---|
| `FROM eclipse-temurin:25-jdk-alpine AS build` | build stage with the full JDK |
| `FROM eclipse-temurin:25-jre-alpine` | final stage: the runtime only |
| `COPY --from=build /src/app.jar ./app.jar` | the jar is the only artefact that crosses over |
| `ENTRYPOINT ["java", "-XX:MaxRAMPercentage=75", "-jar", "app.jar"]` | start the JVM with a container-friendly heap |
| `jdeps --print-module-deps app.jar` | list the JDK modules a jar uses |
| `jlink --add-modules … --output /jre` | build a Java runtime containing only those modules |
| `docker run --entrypoint sh IMAGE -c '…'` | replace the image's entrypoint for one container |

## Hands-on lab

**Instructions.** Verify that the running container uses the unprivileged `app` user, and check which maximum heap the
image's `-XX:MaxRAMPercentage=75` gives a container limited to 512 MB (run `java -XX:+PrintFlagsFinal -version` with
the same option and `-m 512m`).

**Expected result.** `uid=…(app)`, and a `MaxHeapSize` of about 384 MB (75 % of 512 MB).

**Verification.**

<!-- test: contains=(app); contains=MaxHeapSize -->
```bash
docker exec java-multi id
docker run --rm -m 512m --entrypoint java java-multi:1.0 -XX:MaxRAMPercentage=75 -XX:+PrintFlagsFinal -version 2>/dev/null | grep -w MaxHeapSize
```

## Break it

`Dockerfile.broken` builds without errors:

<!-- test: contains=java-multi:broken -->
```bash
docker build -q -f Dockerfile.broken -t java-multi:broken . > /dev/null
docker image ls --filter 'reference=java-multi' --format '{{.Repository}}:{{.Tag}}'
```

But the application never starts:

<!-- test: fail; contains=Unable to access jarfile; output -->
```bash
docker run --rm java-multi:broken 2>&1
```

```text
Error: Unable to access jarfile app.jar
```

## Troubleshoot it

`Unable to access jarfile app.jar`: the JVM started and looked for `app.jar` relative to its **working directory**.
Find out what that is, and where the jar really is:

<!-- test: contains=/opt/app; contains=/app.jar; output -->
```bash
docker run --rm --entrypoint sh java-multi:broken -c 'echo "working directory: $(pwd)"; find / -name app.jar 2>/dev/null; true'
diff Dockerfile.broken Dockerfile || true
```

```text
working directory: /opt/app
/app.jar
0a1
> # stage 1: the JDK compiles and packages the application
6a8
> # stage 2: the JRE only runs it
9,10c11,12
< WORKDIR /opt/app
< COPY --from=build /src/app.jar /app.jar
---
> WORKDIR /app
> COPY --from=build /src/app.jar ./app.jar
```

`WORKDIR` is `/opt/app` but the jar was copied to `/` (an absolute destination ignores `WORKDIR`).

## Fix it

Copy the jar into the working directory with a relative destination (`./app.jar`), as `Dockerfile` does, or use
absolute paths consistently in `COPY` and `ENTRYPOINT`:

<!-- test: contains=java-api listening -->
```bash
docker build -q -t java-multi:fixed . > /dev/null
docker run -d --name java-fixed java-multi:fixed > /dev/null
sleep 2
docker logs java-fixed
docker rm -f java-fixed > /dev/null
```

## Practice challenge

`Dockerfile.jlink` uses `jdeps` to find the modules the jar needs and `jlink` to build a runtime with only those,
running on plain `alpine:3.23`. Build it as `java-jlink:1.0`, find out which modules it contains, check that the API
works, and compare its size with `java-multi:1.0`.

<details>
<summary>Solution</summary>

<!-- test: contains=java.base; contains=jdk.httpserver; contains=java-jlink; output -->
```bash
cd ~/docker-practice/lesson-090
docker build -q -f Dockerfile.jlink -t java-jlink:1.0 . > /dev/null
docker run --rm --entrypoint /opt/jre/bin/java java-jlink:1.0 --list-modules
docker run -d --name java-jlink -p 8093:8080 java-jlink:1.0 > /dev/null
sleep 2
curl -s http://localhost:8093/health; echo
docker image ls --filter 'reference=java-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```text
java.base@25.0.4.1
jdk.httpserver@25.0.4.1
{"status":"ok"}
java-jlink:1.0	78.9MB
java-multi:broken	305MB
java-multi:fixed	305MB
java-multi:1.0	305MB
java-single:1.0	418MB
```

A runtime with two modules instead of the full JRE. The trade-off: if a later version of the code uses another module
(for example `java.sql`), the image must be rebuilt with it, which `jdeps` in the Dockerfile does automatically.

</details>

## Real-world example

Spring Boot services commonly use the two-stage pattern of this lesson with Maven or Gradle in the build stage
(see `Dockerfile.spring-boot` in lesson 043), often combined with Spring Boot's layered jars so that the dependencies
layer is cached and only the application layer changes between releases. Teams that run many small Java services use
`jlink` runtimes to cut image size and pull time further.

## Recap

- Build with the JDK, run with the JRE: `COPY --from=build` only the jar.
- Relative `COPY` destinations and `ENTRYPOINT` paths depend on `WORKDIR`; absolute ones ignore it.
- `--entrypoint` overrides an image's entrypoint to inspect it.
- `jdeps` + `jlink` build a custom runtime with only the modules the application needs.

## Cleanup

<!-- test -->
```bash
docker rm -f java-multi java-jlink java-fixed > /dev/null 2>&1 || true
docker image rm -f java-single:1.0 java-multi:1.0 java-multi:broken java-multi:fixed java-jlink:1.0 > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-090
```

Next: [Lesson 091 · Measuring image size](../091-measuring-image-size/README.md)
