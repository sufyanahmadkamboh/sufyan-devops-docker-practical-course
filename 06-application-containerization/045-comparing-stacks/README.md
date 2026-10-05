# Lesson 045 · Comparing the stacks

> Level 7 · Application containerization · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Lessons 040–044 containerized the same small API in five languages. Every Dockerfile followed the same principles
(official pinned base image, dependencies before code, unprivileged user, exec-form start command), but the results are
very different, because each language needs something different **at run time**. This lesson builds all five side by
side and measures them: image size, memory in use, and what is inside each image.

## Visual

```text
              needs at build time            needs at run time              single-stage image contains
  Node.js     npm + package-lock.json        node runtime + node_modules    runtime + npm + code
  Python      pip + requirements.txt         interpreter + site-packages    interpreter + pip + code
  Go          Go toolchain + go.mod          nothing (static binary)        toolchain + binary   ← most waste
  Java        JDK (javac, Maven/Gradle)      JRE (JVM)                      JDK + jar            ← waste
  PHP         Composer (for frameworks)      PHP-FPM + extensions (+ Nginx) PHP-FPM + code

  the gap between "build time" and "run time" is what multi-stage builds remove (lessons 087–091)
```

| Stack | Start command | Typical production base |
|---|---|---|
| Node.js | `node server.js` | `node:24-alpine` (or a distroless Node.js image) |
| Python | `gunicorn app:app` / `uvicorn main:app` | `python:3.14-slim` |
| Go | `/go-api` | `gcr.io/distroless/static` or `scratch` |
| Java | `java -jar app.jar` | `eclipse-temurin:25-jre-alpine` |
| PHP | `php-fpm` behind Nginx | `php:8.5-fpm-alpine` |

## Lab setup

The five example applications, each with the Dockerfile from its lesson:

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-045 examples/node-api examples/python-api examples/go-api examples/java-api examples/php-app
for pair in node:node-api python:python-api go:go-api java:java-api php:php-app; do
  cp "06-application-containerization/045-comparing-stacks/examples/${pair%%:*}/Dockerfile" ~/docker-practice/lesson-045/"${pair#*:}"/
done
cd ~/docker-practice/lesson-045
ls
```

(`${pair%%:*}` is the part before the colon, `${pair#*:}` the part after it: a shell way to loop over pairs.)

## Demonstration

Build all five. Each folder is its own build context:

<!-- test: contains=built stack-php-app; output -->
```bash
for app in node-api python-api go-api java-api php-app; do
  docker build -q -t "stack-$app:1.0" "$app" > /dev/null && echo "built stack-$app:1.0"
done
```

```text
built stack-node-api:1.0
built stack-python-api:1.0
built stack-go-api:1.0
built stack-java-api:1.0
built stack-php-app:1.0
```

Compare their sizes (`--filter reference=` selects images by name pattern):

<!-- test: contains=stack-go-api; output -->
```bash
docker image ls --filter 'reference=stack-*' --format '{{.Repository}}\t{{.Size}}' | sort -k2 -h
```

```text
stack-php-app	150MB
stack-python-api	209MB
stack-node-api	245MB
stack-java-api	418MB
stack-go-api	492MB
```

Start each one and measure the memory it uses once it is idle:

<!-- test: contains=stack-java; output -->
```bash
for app in node-api python-api go-api java-api php-app; do
  docker run -d --name "stack-${app%-*}" "stack-$app:1.0" > /dev/null
done
sleep 5
docker stats --no-stream --format '{{.Name}}\t{{.MemUsage}}' | sort
```

```text
stack-go	1.633MiB / 15.35GiB
stack-java	20.58MiB / 15.35GiB
stack-node	13.46MiB / 15.35GiB
stack-php	8.859MiB / 15.35GiB
stack-python	64.88MiB / 15.35GiB
```

The numbers depend on your machine and versions; the pattern does not: the Go binary needs a few MB, the JVM and the
two gunicorn workers need tens of MB before serving a single request. The part after `/` is the limit: none was
set, so it is all the memory of the Docker engine (lesson 098 sets limits).

## Command breakdown

| Command | Meaning |
|---|---|
| `docker build -t NAME FOLDER` | build with FOLDER as the context (and FOLDER/Dockerfile) |
| `docker image ls --filter 'reference=stack-*'` | only images whose name matches the pattern |
| `docker stats --no-stream` | one snapshot of CPU, memory, network and disk I/O per container (lesson 095) |
| `--format '{{.Name}}\t{{.MemUsage}}'` | only the name and memory columns |

## Hands-on lab

**Instructions.** Find out which Linux distribution each image is based on, by reading `/etc/os-release` in each one.

**Expected result.** Python's image is Debian (`-slim`), the other four are Alpine.

**Verification.**

<!-- test: contains=Debian; contains=Alpine -->
```bash
for app in node-api python-api go-api java-api php-app; do
  echo "$app: $(docker run --rm "stack-$app:1.0" sh -c '. /etc/os-release; echo $PRETTY_NAME')"
done
```

## Break it

Java's image is the biggest because it contains the JDK. A teammate "optimizes" it by switching the base image to the
smaller JRE (`25-jre-alpine`):

<!-- test: fail; contains=javac: not found; output -->
```bash
sed 's/25-jdk-alpine/25-jre-alpine/' java-api/Dockerfile > java-api/Dockerfile.jre
docker build -f java-api/Dockerfile.jre -t stack-java-api:jre java-api 2>&1 | grep -E 'not found|ERROR' | head -2
test "${PIPESTATUS[0]}" -eq 0
```

```text
#8 0.252 /bin/sh: javac: not found
#8 ERROR: process "/bin/sh -c javac -d classes src/Main.java  && jar --create --file app.jar --main-class Main -C classes .  && rm -rf classes" did not complete successfully: exit code: 127
```

## Troubleshoot it

`javac: not found`, exit code 127 (the shell's code for "command not found"): the JRE contains the JVM to **run**
Java, but not the compiler to **build** it. The Dockerfile compiles inside the image, so it needs the JDK. The same
trap exists for every stack: a Go binary can run on `scratch` but `scratch` cannot compile Go; a Node.js app can run
without TypeScript but cannot be built without it. Check what the JRE image offers:

<!-- test: contains=no javac -->
```bash
docker run --rm eclipse-temurin:25-jre-alpine sh -c 'command -v java; command -v javac || echo "no javac in the JRE"'
```

## Fix it

For now, keep the JDK base (`java-api/Dockerfile`) and accept the size. The real fix is to **build** in a JDK stage
and **run** in a JRE stage of the same Dockerfile: that is a multi-stage build (lessons 087 and 090).

<!-- test: contains=stack-java-api -->
```bash
rm java-api/Dockerfile.jre
docker image ls --filter 'reference=stack-java-api' --format '{{.Repository}}:{{.Tag}} {{.Size}}'
```

## Practice challenge

For the Go image, the program is about 8 MB (lesson 042). How many percent of the image's files are the program
itself? Measure both with `du` inside a container (`du -sk FILE` prints kilobytes; `-x` stays on one file system, so
`/proc` and `/sys` are not counted).

<details>
<summary>Solution</summary>

<!-- test: contains=% of the image; output -->
```bash
binary=$(docker run --rm stack-go-api:1.0 du -sk /usr/local/bin/go-api | cut -f1)
total=$(docker run --rm stack-go-api:1.0 du -skx / 2> /dev/null | cut -f1)
echo "program: $binary kB of $total kB = $((binary * 100 / total)) % of the image"
```

```text
program: 8424 kB of 293808 kB = 2 % of the image
```

A few percent: the rest is the Go toolchain and Alpine, which the program never uses. Lesson 089 brings this image down
to little more than the binary.

</details>

## Real-world example

A platform team that runs services in several languages keeps one "golden" Dockerfile pattern per stack in a shared
template repository: the base image, the user, the health check and the labels are the same everywhere, only the build
steps differ. New services start from the template, and security updates of a base image are rolled out by bumping one
line per template.

## Recap

- The same principles apply to every stack; what differs is what the application needs at run time.
- Measure, do not guess: `docker image ls` for size, `docker stats` for memory.
- Build tools (compilers, package managers) are only needed at build time.
- Swapping in a runtime-only base image breaks the build: separate build and run stages instead (lesson 087).

## Cleanup

<!-- test -->
```bash
docker rm -f stack-node stack-python stack-go stack-java stack-php > /dev/null
docker image rm -f stack-node-api:1.0 stack-python-api:1.0 stack-go-api:1.0 stack-java-api:1.0 stack-php-app:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-045
```

Next: [Lesson 046 · Networking fundamentals](../../07-networking/046-networking-fundamentals/README.md)
