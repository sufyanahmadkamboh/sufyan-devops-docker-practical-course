<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 024 · WORKDIR · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate wrote the menu service without `WORKDIR`, with a `cd` instead:

```bash
cat Dockerfile.broken
docker build -q -f Dockerfile.broken -t menu:broken . > /dev/null
docker run --rm menu:broken
```

```text
# The menu service: prints the menu
FROM alpine:3.23
COPY menu.csv /app/
RUN cd /app
CMD ["cat", "menu.csv"]
cat: can't open 'menu.csv': No such file or directory
```

The build succeeded, the container fails.

## Troubleshoot it

`can't open 'menu.csv'`: the file was copied, so the question is where the container is looking for it. Check the
image's working directory and where the file really is:

```bash
echo "workdir: [$(docker image inspect --format '{{.Config.WorkingDir}}' menu:broken)]"
docker run --rm menu:broken sh -c 'pwd; ls /app/menu.csv'
```

```text
workdir: [/]
/
/app/menu.csv
```

The image's working directory is `/` (the default when no `WORKDIR` is set), but the file is in `/app`. The
`RUN cd /app` step changed the directory only for its own shell, which ended with the step; it left nothing in the
image.

## Fix it

Replace the `cd` with `WORKDIR`, which is recorded in the image:

```bash
diff Dockerfile.broken Dockerfile.fixed || true
docker build -q -f Dockerfile.fixed -t menu:fixed . > /dev/null
docker run --rm menu:fixed
```

```text
3,4c3,4
< COPY menu.csv /app/
< RUN cd /app
---
> WORKDIR /app
> COPY menu.csv .
item,price
espresso,2.50
cappuccino,3.20
flat white,3.40
```

When you really need another directory for one step, `cd` inside that `RUN`: `RUN cd /tmp && tar -xzf tools.tgz`.
