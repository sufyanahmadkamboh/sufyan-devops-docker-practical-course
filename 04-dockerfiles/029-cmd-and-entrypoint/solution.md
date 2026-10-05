<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 029 · CMD and ENTRYPOINT together · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write the entrypoint-script pattern used by official images: a `docker-entrypoint.sh` that prints
`preparing the cafe…` and then runs whatever command it receives with `exec "$@"`, with `CMD ["price", "espresso"]` as
the default. Verify that the default works and that `docker run IMAGE price "flat white"` works too.

## Solution

```bash
cd ~/docker-practice/lesson-029
printf '#!/bin/sh\nset -e\necho "preparing the cafe..."\nexec "$@"\n' > docker-entrypoint.sh
cat > Dockerfile.script <<'EOF'
FROM alpine:3.23
COPY menu.csv /app/
COPY --chmod=0755 price.sh /usr/local/bin/price
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["price", "espresso"]
EOF
docker build -q -f Dockerfile.script -t price:script . > /dev/null
docker run --rm price:script
docker run --rm price:script price "flat white"
```

```text
preparing the cafe...
2.50 EUR
preparing the cafe...
3.40 EUR
```

The script does its preparation, then `exec "$@"` *replaces* the shell with the command (the `CMD`, or your run
arguments), so the real program becomes the container's main process and receives signals from `docker stop`.
