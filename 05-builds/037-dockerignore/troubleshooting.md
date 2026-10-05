<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 037 · .dockerignore · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate writes their own short `.dockerignore`, expecting `*.log` to exclude every log file, as it would in
`.gitignore`:

```bash
cd ~/docker-practice/lesson-037
printf '.env\nnode_modules\n*.log\n' > .dockerignore
docker build -q -t ignore-demo:logs . > /dev/null
docker run --rm ignore-demo:logs find /app/logs -type f
```

```text
/app/logs/debug/app.log
```

## Troubleshoot it

The log file is in the image although `*.log` is in `.dockerignore`. The rules differ from Git's: in `.gitignore` a
pattern without a slash matches at any depth, but in `.dockerignore` **every pattern is anchored at the root of the
context**. `*.log` therefore means "`.log` files directly in the context root", and `logs/debug/app.log` does not match.
To see exactly what a `.dockerignore` lets through, list the image (or a throw-away `COPY . .` image) as above, and
compare with the folder:

```bash
find . -name '*.log'
```

## Fix it

Use `**` for "any number of folders":

```bash
printf '.env\nnode_modules\n**/*.log\n' > .dockerignore
docker build -q -t ignore-demo:logs . > /dev/null
[ -z "$(docker run --rm ignore-demo:logs find /app -name '*.log')" ] && echo "no log files in the image"
```
