<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 029 · CMD and ENTRYPOINT together · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Someone "simplifies" the Dockerfile to the shell form of `ENTRYPOINT`:

```bash
printf 'FROM alpine:3.23\nCOPY menu.csv /app/\nCOPY --chmod=0755 price.sh /usr/local/bin/price\nENTRYPOINT price\nCMD ["espresso"]\n' > Dockerfile.shell
docker build -q -f Dockerfile.shell -t price:shell . > /dev/null 2>&1
docker run --rm price:shell cappuccino
```

```text
/usr/local/bin/price: line 4: 1: usage: price ITEM
```

## Troubleshoot it

`usage: price ITEM`: the script ran but received **no** argument, neither the `CMD` nor `cappuccino`. Look at what the
container executed:

```bash
docker run --name price-shell price:shell cappuccino > /dev/null 2>&1 || true
docker container inspect --format 'path={{.Path}} args={{json .Args}}' price-shell
docker rm price-shell > /dev/null
docker build --check -f Dockerfile.shell . 2>&1 | grep -o "WARNING: [A-Za-z]*"
```

```text
path=/bin/sh args=["-c","price","cappuccino"]
WARNING: JSONArgsRecommended
```

The shell form wraps the entrypoint in `/bin/sh -c price`. The extra word `cappuccino` is given to the shell (as its
`$0`), not to `price`, so it is lost. `docker build --check` warns about this combination (`JSONArgsRecommended`).

## Fix it

```bash
sed -i.bak 's/^ENTRYPOINT price$/ENTRYPOINT ["price"]/' Dockerfile.shell && rm Dockerfile.shell.bak
docker build -q -f Dockerfile.shell -t price:shell . > /dev/null
docker run --rm price:shell cappuccino
```
