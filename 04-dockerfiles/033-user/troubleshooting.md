<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 033 · USER · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The first attempt at a non-root order service only adds `USER`:

```bash
docker build -q -f Dockerfile.broken -t orders:broken . > /dev/null
docker run --rm orders:broken espresso
```

```text
./take-order.sh: line 4: can't create /app/orders.log: Permission denied
```

## Troubleshoot it

`can't create /app/orders.log: Permission denied`: the script runs, but cannot create its file. Compare the user with
the owner of the folder:

```bash
docker run --rm --entrypoint sh orders:broken -c 'id; ls -ld /app; ls -l /app'
```

```text
uid=10001(appuser) gid=101(cafe) groups=101(cafe),101(cafe)
drwxr-xr-x    1 root     root          4096 Oct  5 11:59 /app
total 4
-rwxr-xr-x    1 root     root           204 Oct  5 11:59 take-order.sh
```

`WORKDIR` and `COPY` ran as root, so `/app` belongs to root and only root may create files in it. Under root, the
mistake was invisible, because root may write everywhere.

Do not "fix" it by going back to root (`USER root`, `docker run --user 0`): that removes the protection you wanted.

## Fix it

Give the user exactly one writable place, and leave the code owned by root:

```bash
diff Dockerfile.broken Dockerfile.fixed || true
docker build -q -f Dockerfile.fixed -t orders:fixed . > /dev/null
docker run --rm orders:fixed espresso
```

```text
5a6,8
> # the code stays owned by root (read-only for appuser); only the data folder is writable
> RUN mkdir /app/data && chown appuser:cafe /app/data
> ENV ORDER_LOG=/app/data/orders.log
16:55:06 espresso
```

The application can no longer modify its own code (an attacker cannot either), and its data can live in a volume
mounted at `/app/data` (lesson 055).
