<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 090 · Multi-stage builds for Java · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

`Dockerfile.broken` builds without errors:

```bash
docker build -q -f Dockerfile.broken -t java-multi:broken . > /dev/null
docker image ls --filter 'reference=java-multi' --format '{{.Repository}}:{{.Tag}}'
```

But the application never starts:

```bash
docker run --rm java-multi:broken 2>&1
```

```text
Error: Unable to access jarfile app.jar
```

## Troubleshoot it

`Unable to access jarfile app.jar`: the JVM started and looked for `app.jar` relative to its **working directory**.
Find out what that is, and where the jar really is:

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

```bash
docker build -q -t java-multi:fixed . > /dev/null
docker run -d --name java-fixed java-multi:fixed > /dev/null
sleep 2
docker logs java-fixed
docker rm -f java-fixed > /dev/null
```
