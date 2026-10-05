<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 043 · Containerizing a Java application · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Our single-stage image ships the whole JDK. Find out how much of it is the compiler toolchain: compare the size of the
`eclipse-temurin:25-jdk-alpine` image with `eclipse-temurin:25-jre-alpine` (the runtime only), and check that the JRE
image has no `javac`.

## Solution

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
