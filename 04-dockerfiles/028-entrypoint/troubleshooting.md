<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 028 · ENTRYPOINT · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

You want to look inside the image, so you ask for a shell the usual way:

```bash
docker run --rm price:1.0 sh
```

```text
unknown item: sh
```

## Troubleshoot it

`unknown item: sh`: the message comes from `price.sh`, so the script ran and received `sh` as an item name. With an
`ENTRYPOINT`, the words after the image name are arguments, never a new command. Check what the container really
executed:

```bash
docker run --name price-check price:1.0 sh > /dev/null 2>&1 || true
docker container inspect --format 'path={{.Path}} args={{json .Args}}' price-check
docker rm price-check > /dev/null
```

```text
path=price args=["sh"]
```

## Fix it

Replace the entrypoint for this one container; the arguments after the image name now go to the new program:

```bash
docker run --rm --entrypoint sh price:1.0 -c 'ls /app/menu.csv /usr/local/bin/price'
```

```text
/app/menu.csv
/usr/local/bin/price
```

For an interactive shell, `docker run --rm -it --entrypoint sh price:1.0`.
