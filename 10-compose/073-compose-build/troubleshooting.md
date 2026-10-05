<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 073 · Building images with Compose · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A developer changes the API's default greeting and restarts the stack:

```bash
sed -i.bak 's/Hello from Python/Hello from version 1.4.0/' app.py && rm app.py.bak
grep -c "Hello from version 1.4.0" app.py
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/
```

```text
1
{"hostname":"d866db03be30","message":"Hello from Python"}
```

## Troubleshoot it

The file is changed, the answer is old. The code inside an image is a copy made at build time (`COPY app.py .`), and
`up` reuses the existing image. Compare the image's creation time with the file:

```bash
docker image inspect cafe-api:1.4.0 --format 'image built: {{.Created}}'
docker compose exec api grep -o "Hello from [A-Za-z0-9. ]*" app.py
```

```text
image built: 2026-10-05T17:11:02.737714484Z
Hello from Python
```

The container runs the code of the image, which still has the old `app.py`.

## Fix it

```bash
docker compose up -d --build --quiet-build 2> /dev/null
curl -s localhost:8080/
```

```text
{"hostname":"74c930a4170b","message":"Hello from version 1.4.0"}
```

The rebuild was fast: `requirements.txt` did not change, so the `pip install` layer came from the cache, and only the
`COPY app.py` layer and the ones after it were rebuilt (lesson 039). For fast feedback during development, Compose can
also sync or rebuild automatically (`docker compose watch`, with a `develop:` section).
