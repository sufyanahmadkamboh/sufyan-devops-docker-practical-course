# Lesson 041 · Containerizing a Python application

> Level 7 · Application containerization · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

How to containerize a Python web API (Flask here; FastAPI works the same way with `uvicorn` instead of `gunicorn`):
a slim official base image, pinned requirements installed before the code, two Python settings that matter in
containers, an unprivileged user, and a **production server** listening on `0.0.0.0`. The last point is the most common
reason a containerized Python app "runs but cannot be reached".

## Visual

```text
  python-api/                       Dockerfile
  ├── requirements.txt  ──▶  FROM python:3.14-slim
  │   flask==3.1.3            ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
  │   gunicorn==26.2.0        RUN useradd … appuser
  │   redis==8.1.0            COPY requirements.txt .  ─▶ RUN pip install --no-cache-dir -r requirements.txt
  └── app.py            ──▶   COPY app.py .
                              USER appuser
                              CMD ["gunicorn","--bind","0.0.0.0:5000","--workers","2","app:app"]

  container                                           your computer
  ┌───────────────────────────────────────┐
  │ gunicorn master ─┬─ worker  :5000     │◀──── -p 8082:5000 ──── curl localhost:8082   ✓ (0.0.0.0)
  │                  └─ worker            │
  │ flask run (dev)   127.0.0.1:5000      │◀──── -p 8082:5000 ──── curl localhost:8082   ✗ (only inside)
  └───────────────────────────────────────┘
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-041 examples/python-api
cp -r 06-application-containerization/041-containerize-python/examples/. ~/docker-practice/lesson-041/
cd ~/docker-practice/lesson-041
cat Dockerfile
```

## Demonstration

<!-- test: contains=python-api; output -->
```bash
docker build -q -t python-api:1.0 . > /dev/null
docker image ls python-api
docker run -d --name python-api -p 8082:5000 python-api:1.0 > /dev/null
```

```text
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
python-api:1.0   66c950d9c447        209MB         50.5MB        
```

<!-- test: retry=10; contains=Hello from Python; output -->
```bash
curl -s http://localhost:8082/
```

```text
{"hostname":"8654d34324d9","message":"Hello from Python"}
```

Gunicorn's start-up lines appear in the logs immediately, thanks to `PYTHONUNBUFFERED=1`:

<!-- test: contains=Listening at: http://0.0.0.0:5000; output -->
```bash
docker logs python-api 2>&1 | head -2
```

```text
[2026-10-05 17:05:57 +0000] [1] [INFO] Starting gunicorn 26.2.0
[2026-10-05 17:05:57 +0000] [1] [INFO] Listening at: http://0.0.0.0:5000 (1)
```

## Command breakdown

| Instruction | Why |
|---|---|
| `FROM python:3.14-slim` | Debian-based and small; the `-alpine` variant is smaller but uses musl, which some wheels do not support |
| `PYTHONDONTWRITEBYTECODE=1` | do not write `.pyc` files into the container |
| `PYTHONUNBUFFERED=1` | print logs immediately instead of buffering them (otherwise `docker logs` lags or loses lines) |
| `pip install --no-cache-dir` | do not keep pip's download cache in the layer |
| `useradd --uid 10001 appuser` + `USER appuser` | run without root |
| `gunicorn --bind 0.0.0.0:5000` | a production WSGI server, listening on all interfaces of the container |

## Hands-on lab

**Instructions.** Show the processes of the running container from the host with `docker top` (the slim image has no
`ps`), and check which user they run as.

**Expected result.** Three `gunicorn` processes (one master, two workers), all running as uid `10001`.

**Verification.**

<!-- test: contains=gunicorn -->
```bash
docker top python-api -o pid,user,args
```

(`docker top` shows the host's view, where the user appears as `10001` because the host has no user named `appuser`.)

## Break it

A developer starts the image with Flask's own development server instead of gunicorn, as they do on their laptop:

<!-- test: fail; anyof=Empty reply from server||Connection reset||Recv failure; output -->
```bash
docker run -d --name python-dev -p 8083:5000 python-api:1.0 flask --app app run > /dev/null
sleep 3
curl -sS http://localhost:8083/ 2>&1
```

```text
curl: (52) Empty reply from server
```

## Troubleshoot it

The container is running, the port is published, and still no response. Read what the application says about itself:

<!-- test: contains=127.0.0.1:5000; output -->
```bash
docker logs python-dev 2>&1 | grep Running
```

```text
 * Running on http://127.0.0.1:5000
```

`127.0.0.1` is the container's **own** loopback interface. Published traffic arrives through the container's network
interface (`eth0`), not through its loopback, so a server bound to `127.0.0.1` can only be reached from inside the
container. On a laptop without Docker, `127.0.0.1` is exactly right, which is why this works locally and fails in a
container. Prove it from inside:

<!-- test: contains=Hello from Python -->
```bash
docker exec python-dev python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/').read().decode())"
```

## Fix it

Listen on all interfaces, `0.0.0.0`. For the development server that is `--host 0.0.0.0`; the image's default command
(gunicorn) already does it:

<!-- test: contains=Hello from Python -->
```bash
docker rm -f python-dev > /dev/null
docker run -d --name python-dev -p 8083:5000 python-api:1.0 flask --app app run --host 0.0.0.0 > /dev/null
sleep 3
curl -s http://localhost:8083/
```

The development server is fine for debugging, but it prints `WARNING: This is a development server` for a reason: in
the image, keep gunicorn (or uvicorn for FastAPI: `uvicorn main:app --host 0.0.0.0 --port 8000`).

## Practice challenge

Gunicorn also reads options from the environment variable `GUNICORN_CMD_ARGS`. Without rebuilding the image, try to
start a container with **4** workers that way (on port 8084) and count the gunicorn processes. Does it work? If not,
find another way that does, still without rebuilding.

<details>
<summary>Solution</summary>

<!-- test: contains=with GUNICORN_CMD_ARGS: 3; contains=with a new command: 5; output -->
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

</details>

## Real-world example

A FastAPI service is typically containerized with the same structure: `python:3.14-slim`, `pip install -r
requirements.txt` from a locked file (pip-tools, Poetry export or uv), the code last, and
`CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`. The number of workers is set per environment
through a variable, so the same image runs with 1 worker on a laptop and 4 on a production node.

## Recap

- Slim base image, requirements before code, `--no-cache-dir`, an unprivileged user.
- `PYTHONUNBUFFERED=1` makes logs appear in `docker logs` immediately.
- Run a production server (gunicorn, uvicorn), not the framework's development server.
- A server bound to `127.0.0.1` cannot be reached through a published port: bind to `0.0.0.0`.

## Cleanup

<!-- test -->
```bash
docker rm -f python-api python-dev python-4w > /dev/null 2>&1 || true
docker image rm -f python-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-041
```

Next: [Lesson 042 · Containerizing a Go application](../042-containerize-go/README.md)
