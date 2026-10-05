# Lesson 043 · Containerizing a Java application

> Level 7 · Application containerization · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

How to containerize a Java service: compile and package it into an executable **jar** inside an official JDK image
(Eclipse Temurin), run it with `java -jar` as an unprivileged user, and understand how the JVM sizes its memory inside
a container. The example is a plain JDK HTTP server, so the build needs no Maven download; the Spring Boot pattern,
which follows the same principles, is shown as an annotated Dockerfile.

## Visual

```text
  java-api/src/Main.java         Dockerfile (single stage)                image java-api:1.0
             │            FROM eclipse-temurin:25-jdk-alpine            ┌──────────────────────────────┐
             └──────────▶ COPY src ./src                                │ JDK: compiler, jar tool,     │
                          RUN javac -d classes …                        │ JVM, Alpine                  │
                              && jar --create --file app.jar            ├──────────────────────────────┤
                                     --main-class Main -C classes .     │ /app/app.jar                 │
                          USER app                                      └──────────────────────────────┘
                          CMD ["java","-jar","app.jar"]

  JVM in a container:  docker run -m 512m …  ─▶  the JVM sees 512 MB  ─▶  default max heap = 25 % = 128 MB
                       -XX:MaxRAMPercentage=75                         ─▶  max heap = 384 MB
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-043 examples/java-api
cp 06-application-containerization/043-containerize-java/examples/Dockerfile* ~/docker-practice/lesson-043/
cd ~/docker-practice/lesson-043
ls . src
```

## Demonstration

<!-- test: contains=java-api; output -->
```bash
docker build -q -t java-api:1.0 . > /dev/null
docker image ls java-api
docker run -d --name java-api -p 8087:8080 java-api:1.0 > /dev/null
```

```text
IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
java-api:1.0   0f84c49140ed        418MB          110MB        
```

<!-- test: retry=15; contains=Hello from Java; output -->
```bash
curl -s http://localhost:8087/
```

```text
{"message":"Hello from Java","hostname":"e5807842f8d3"}
```

The JVM is container-aware: it reads the container's CPU and memory limits, not the host's. Start the image with a
512 MB memory limit and ask the JVM for its maximum heap size:

<!-- test: contains=MaxHeapSize; output -->
```bash
docker run --rm -m 512m java-api:1.0 java -XX:+PrintFlagsFinal -version 2>/dev/null | grep -w MaxHeapSize
```

```text
   size_t MaxHeapSize                              = 134217728                                 {product} {ergonomic}
```

134217728 bytes = 128 MB: by default the JVM uses only 25 % of the container's memory for the heap. A container with a
memory limit usually runs just the JVM, so teams raise it with `-XX:MaxRAMPercentage`.

**Spring Boot.** A Spring Boot service is built by Maven or Gradle instead of `javac`, but the same rules apply: build definition first
for caching, an unprivileged user, a memory setting for the JVM. Spring Boot can also split its jar into layers
(dependencies, loader, application), so that a code change only rebuilds and re-pulls the small application layer.
This is the usual shape (an illustration; the multi-stage syntax `AS build` / `COPY --from=build` is lesson 087):

<!-- test: contains=JarLauncher -->
```bash
cat Dockerfile.spring-boot
```

## Command breakdown

| Instruction / option | Why |
|---|---|
| `FROM eclipse-temurin:25-jdk-alpine` | an official OpenJDK build (Java 25 LTS) with the compiler |
| `javac -d classes` + `jar --create --main-class Main` | compile, then package into an executable jar |
| `adduser -S app` + `USER app` | an unprivileged system user (Alpine's `adduser`) |
| `CMD ["java", "-jar", "app.jar"]` | exec form: the JVM is PID 1 and handles `SIGTERM` |
| `-m 512m` | a memory limit for the container (lesson 098) |
| `-XX:MaxRAMPercentage=75` | let the heap use 75 % of the container's memory |

## Hands-on lab

**Instructions.** Without rebuilding, start the image with a 512 MB limit and `JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75`
(the JVM reads options from this variable), and check the new maximum heap.

**Expected result.** `MaxHeapSize` of about 384 MB (402653184 bytes, the JVM rounds to its alignment), and a line
`Picked up JAVA_TOOL_OPTIONS` proving the variable was read.

**Verification.**

<!-- test: contains=Picked up JAVA_TOOL_OPTIONS; contains=MaxHeapSize -->
```bash
docker run --rm -m 512m -e JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=75 java-api:1.0 \
  java -XX:+PrintFlagsFinal -version 2>&1 | grep -E 'Picked up|MaxHeapSize '
```

## Break it

A colleague writes the start command by hand, as they remember it from the project's run configuration:

<!-- test: fail; contains=Could not find or load main class; output -->
```bash
docker run --rm java-api:1.0 java -cp app.jar main 2>&1
```

```text
Error: Could not find or load main class main
Caused by: java.lang.ClassNotFoundException: main
```

## Troubleshoot it

`Could not find or load main class main`: the JVM started, opened `app.jar`, and found no class called `main`. Java
class names are case-sensitive and include the package. List what the jar really contains, and which main class its
manifest declares:

<!-- test: contains=Main.class; contains=Main-Class: Main; output -->
```bash
docker run --rm java-api:1.0 sh -c 'jar --list --file app.jar; unzip -p app.jar META-INF/MANIFEST.MF'
```

```text
META-INF/
META-INF/MANIFEST.MF
Main.class
Manifest-Version: 1.0
Created-By: 25.0.4.1 (Eclipse Adoptium)
Main-Class: Main
```

## Fix it

Use the exact class name, or better, let the manifest decide with `java -jar` (what the image's `CMD` does):

<!-- test: contains=java-api listening -->
```bash
docker run --rm -d --name java-fixed java-api:1.0 java -cp app.jar Main > /dev/null
sleep 2
docker logs java-fixed
docker rm -f java-fixed > /dev/null
```

## Practice challenge

Our single-stage image ships the whole JDK. Find out how much of it is the compiler toolchain: compare the size of the
`eclipse-temurin:25-jdk-alpine` image with `eclipse-temurin:25-jre-alpine` (the runtime only), and check that the JRE
image has no `javac`.

<details>
<summary>Solution</summary>

<!-- test: contains=javac: not found; output -->
```bash
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' eclipse-temurin
docker run --rm eclipse-temurin:25-jre-alpine javac -version 2>&1 || true
```

```text
eclipse-temurin:25-jre-alpine  306MB
eclipse-temurin:25-jdk-alpine  419MB
/__cacert_entrypoint.sh: exec: line 123: javac: not found
```

About 110 MB of the image are only needed to **build**. The JRE can run the jar but not compile it: compile in a JDK
stage, run in a JRE stage (lesson 090).

</details>

## Real-world example

Java services in containers are often killed by the kernel's out-of-memory killer (exit code 137) although "the heap
is only 1 GB": the JVM also needs memory for threads, metaspace and buffers outside the heap. Teams set the container
limit, then `-XX:MaxRAMPercentage` between 50 and 75, and watch the container's real memory use (lesson 095) instead of
copying `-Xmx` values from the days of dedicated servers.

## Recap

- Compile and package inside an official JDK image; run with `java -jar` as an unprivileged user.
- The JVM respects container limits; by default the heap is 25 % of the container's memory.
- Set `-XX:MaxRAMPercentage` (or `JAVA_TOOL_OPTIONS`) instead of a fixed `-Xmx`.
- `Could not find or load main class`: check the class name and the jar's manifest.

## Cleanup

<!-- test -->
```bash
docker rm -f java-api > /dev/null
docker image rm -f java-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-043
```

Next: [Lesson 044 · Containerizing a PHP application](../044-containerize-php/README.md)
