<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 043 · Containerizing a Java application · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague writes the start command by hand, as they remember it from the project's run configuration:

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

```bash
docker run --rm -d --name java-fixed java-api:1.0 java -cp app.jar Main > /dev/null
sleep 2
docker logs java-fixed
docker rm -f java-fixed > /dev/null
```
