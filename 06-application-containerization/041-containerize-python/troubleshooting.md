<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 041 · Containerizing a Python application · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A developer starts the image with Flask's own development server instead of gunicorn, as they do on their laptop:

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

```bash
docker exec python-dev python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/').read().decode())"
```

## Fix it

Listen on all interfaces, `0.0.0.0`. For the development server that is `--host 0.0.0.0`; the image's default command
(gunicorn) already does it:

```bash
docker rm -f python-dev > /dev/null
docker run -d --name python-dev -p 8083:5000 python-api:1.0 flask --app app run --host 0.0.0.0 > /dev/null
sleep 3
curl -s http://localhost:8083/
```

The development server is fine for debugging, but it prints `WARNING: This is a development server` for a reason: in
the image, keep gunicorn (or uvicorn for FastAPI: `uvicorn main:app --host 0.0.0.0 --port 8000`).
