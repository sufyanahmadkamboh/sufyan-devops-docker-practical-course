<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 041 · Containerizing a Python application · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Gunicorn also reads options from the environment variable `GUNICORN_CMD_ARGS`. Without rebuilding the image, try to
start a container with **4** workers that way (on port 8084) and count the gunicorn processes. Does it work? If not,
find another way that does, still without rebuilding.

## Solution

```bash
docker run -d --name python-4w -p 8084:5000 -e GUNICORN_CMD_ARGS="--workers 4" python-api:1.0 > /dev/null
sleep 3
echo "with GUNICORN_CMD_ARGS: $(docker top python-4w | grep -c gunicorn) gunicorn processes"
docker rm -f python-4w > /dev/null
docker run -d --name python-4w -p 8084:5000 python-api:1.0 gunicorn --bind 0.0.0.0:5000 --workers 4 app:app > /dev/null
sleep 3
echo "with a new command: $(docker top python-4w | grep -c gunicorn) gunicorn processes"
```

```text
with GUNICORN_CMD_ARGS: 3 gunicorn processes
with a new command: 5 gunicorn processes
```

The variable did not help: gunicorn applies `GUNICORN_CMD_ARGS` first and the command-line options after it, so the
`--workers 2` in the image's `CMD` wins. Replacing the command (everything after the image name) works. A cleaner
design leaves `--workers` out of `CMD`, so that the variable (or a gunicorn config file) controls it per environment.
