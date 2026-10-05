<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 045 · Comparing the stacks · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Java's image is the biggest because it contains the JDK. A teammate "optimizes" it by switching the base image to the
smaller JRE (`25-jre-alpine`):

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

```bash
docker run --rm eclipse-temurin:25-jre-alpine sh -c 'command -v java; command -v javac || echo "no javac in the JRE"'
```

## Fix it

For now, keep the JDK base (`java-api/Dockerfile`) and accept the size. The real fix is to **build** in a JDK stage
and **run** in a JRE stage of the same Dockerfile: that is a multi-stage build (lessons 087 and 090).

```bash
rm java-api/Dockerfile.jre
docker image ls --filter 'reference=stack-java-api' --format '{{.Repository}}:{{.Tag}} {{.Size}}'
```
