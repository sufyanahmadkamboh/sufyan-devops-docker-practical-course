<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 043 · Containerizing a Java application · challenge

> The full lesson: [README.md](README.md)

## Practice challenge

Our single-stage image ships the whole JDK. Find out how much of it is the compiler toolchain: compare the size of the
`eclipse-temurin:25-jdk-alpine` image with `eclipse-temurin:25-jre-alpine` (the runtime only), and check that the JRE
image has no `javac`.

The solution is in [solution.md](solution.md).
