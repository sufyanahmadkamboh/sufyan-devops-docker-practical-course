# Lesson 002 · Why containers?

> Level 1 · Container fundamentals · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

An application is never just its code. It needs a runtime, libraries, system packages and configuration, all in the
right versions. The traditional way installs them on each server by hand, and every server slowly becomes different.
A container image ships the application **and** that whole stack, so what you tested is exactly what runs.

## Visual

```text
 What an application really needs            Traditional deployment            Container deployment

   Application code                           server 1: Python 3.11, lib 1.2     image cafe-api:1.4.0
 + Runtime (Python 3.14)                      server 2: Python 3.12, lib 1.4       = code + runtime + libraries
 + Libraries (Flask 3.1)                      server 3: Python 3.11, lib 1.3         + dependencies + config defaults
 + System dependencies (libpq, CA certs)       → "works on server 2 only"          → identical everywhere it runs
 + Configuration (ports, URLs)                manual installs, slow drift          built once, run anywhere
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-002 examples/python-api
cd ~/docker-practice/lesson-002
ls
```

A small Flask API: `app.py` and its `requirements.txt` (Flask 3.1.3, Redis 8.1.0, Gunicorn 26.2.0).

## Demonstration

On a "server" with the wrong stack, the application cannot even start. A bare Python image plays that server:

<!-- test: fail; contains=ModuleNotFoundError; output -->
```bash
docker run --rm -v "$(pwd):/app:ro" -w /app python:3.14-slim python -c "import app" 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
ModuleNotFoundError: No module named 'flask'
```

`ModuleNotFoundError: No module named 'flask'`: the code is there, its dependencies are not. That is the traditional
problem: the server must be prepared exactly right. Now package the dependencies with the code, the container way
(Dockerfiles are lesson 022; this one is three lines):

<!-- test: contains=cafe-api; output -->
```bash
printf 'FROM python:3.14-slim\nWORKDIR /app\nCOPY . .\nRUN pip install --no-cache-dir -r requirements.txt\n' > Dockerfile
docker build -q -t cafe-api:1.0 . > /dev/null
docker image ls cafe-api
```

```text
IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
cafe-api:1.0   5508aca87d9f        223MB         54.2MB        
```

<!-- test: contains=Hello from Python; output -->
```bash
docker run --rm cafe-api:1.0 python -c "import app; print(app.app.test_client().get('/').json)"
```

```text
{'hostname': '2d05f2a4d637', 'message': 'Hello from Python'}
```

The image contains the code, Python 3.14 and the exact library versions: it runs the same on any machine with Docker.

## Command breakdown

| Part | What it does |
|---|---|
| `-v "$(pwd):/app:ro"` | make the current folder visible inside the container, read-only (a bind mount, lesson 054): the container cannot leave files in your folder |
| `-w /app` | run the command in that folder |
| `docker build -t NAME:TAG .` | package the folder's Dockerfile into an image (lesson 035) |
| `docker run IMAGE COMMAND` | run a command in a new container of that image |

## Hands-on lab

**Instructions.** Check which Flask version is inside the image, and which (if any) is on your own computer.

**Expected result.** `3.1.3` in the image, whatever is (or is not) installed locally.

**Verification.**

<!-- test: contains=3.1.3 -->
```bash
cd ~/docker-practice/lesson-002
docker run --rm cafe-api:1.0 pip show flask | grep Version
```

## Break it

A teammate "upgrades" the server by hand to a different Flask version and only tests on their laptop:

<!-- test: contains=3.0.3; output -->
```bash
docker run --rm python:3.14-slim sh -c 'pip install -q flask==3.0.3 2>/dev/null; pip show flask | grep Version'
```

```text
Version: 3.0.3
```

## Troubleshoot it

Every hand-installed environment drifts: this "server" now has Flask 3.0.3, the tested build has 3.1.3. Bugs that only
happen in one environment come from exactly this. Compare the two environments:

<!-- test: contains=3.1.3 -->
```bash
docker run --rm cafe-api:1.0 pip show flask | grep Version
```

## Fix it

Never change a running environment by hand. Change the pinned version in `requirements.txt`, rebuild the image, test it,
and ship the new image: the version is recorded in Git and identical everywhere.

<!-- test: contains=3.1.3 -->
```bash
grep -i flask requirements.txt
```

## Practice challenge

Prove the image is self-contained: run the API's health check from the image with **no** folder mounted from your
computer.

<details>
<summary>Solution</summary>

<!-- test: contains=ok; output -->
```bash
cd ~/docker-practice/lesson-002
docker run --rm cafe-api:1.0 python -c "import app; print(app.app.test_client().get('/health').json)"
```

```text
{'status': 'ok'}
```

Everything the application needs is inside the image: code, runtime and libraries.

</details>

## Real-world example

A company runs 40 services written in four languages. Without containers, each server needs the right mix of runtimes
and versions, and upgrades are risky. With containers, every service brings its own stack; servers only need Docker (or
Kubernetes), and a service upgrade is "deploy the new image, keep the old one to roll back".

## Recap

- An application needs code + runtime + libraries + system dependencies + configuration.
- Installing them by hand on servers causes drift and "works on my machine" bugs.
- A container image packages the whole stack once; every environment runs the same image.

## Cleanup

<!-- test -->
```bash
docker image rm -f cafe-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-002
```

Next: [Lesson 003 · Docker vs virtual machines](../003-docker-vs-vms/README.md)
