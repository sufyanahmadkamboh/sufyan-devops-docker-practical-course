# Troubleshooting problem 11 · Missing environment variable

> ⏱ 15 minutes · run every command from the course folder · related lessons: 014, 059, 060

## Problem

The billing service starts on a developer's machine but stops immediately on the test server with exit code 1. The
deployment script was copied from another service and does not pass any configuration.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-11 17-troubleshooting/11-missing-environment-variable/examples
cd ~/docker-practice/trouble-11
docker run -d --name billing -p 8080:8080 -v "$(pwd):/app" -w /app python:3.14-slim python app.py > /dev/null
```

<!-- test: contains=Exited (1); output -->
```bash
sleep 2
docker ps -a --filter name=billing --format '{{.Names}}: {{.Status}}'
```

```text
billing: Exited (1) 1 second ago
```

## Investigation

**1. What did it print?** An exit code 1 is the application's own failure, so its logs explain it:

<!-- test: contains=KeyError; output -->
```bash
docker logs billing 2>&1 | tail -4
```

```text
    DATABASE_URL = os.environ["DATABASE_URL"]          # required: fail at start if it is missing
                   ~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "<frozen os>", line 709, in __getitem__
KeyError: 'DATABASE_URL'
```

**2. What environment did the container get?**

<!-- test: absent=DATABASE_URL; output -->
```bash
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' billing
```

```text
PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PYTHON_VERSION=3.14.8
PYTHON_SHA256=c2215904f02b175596dc49351585104f4bc20341e1c47378b26a2c274360ce73
```

Only the variables of the base image (`PATH`, `LANG`, Python's own): nothing from the application.

**3. What does the application expect?**

<!-- test: contains=DATABASE_URL; output -->
```bash
grep -n 'os.environ' app.py
```

```text
5:DATABASE_URL = os.environ["DATABASE_URL"]          # required: fail at start if it is missing
6:CURRENCY = os.environ.get("CURRENCY", "EUR")       # optional, with a default
```

## Commands

| Command | What it tells you |
|---|---|
| `docker logs NAME` | the application's error, even after it exited |
| `docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' NAME` | every variable the container was given |
| `docker exec NAME env` | the environment of a *running* container |
| `docker run --rm --env-file FILE IMAGE env` | what a variables file really sets, before you deploy |

## Output interpretation

`KeyError: 'DATABASE_URL'` at `os.environ["DATABASE_URL"]` means the variable does not exist in the process's
environment. Node.js shows `undefined`, Go an empty string, Java `null`: in those languages the app may start and fail
later, so failing early (as here) is the better design. `Exited (1)` is an application error, not a Docker error.

## Root cause

The container was started without the required `DATABASE_URL`. Environment variables are not inherited from the
server's shell: each container gets only what `-e`, `--env-file`, Compose or the image's `ENV` give it.

## Fix

Pass the configuration from a file kept next to the deployment (lesson 060):

<!-- test: contains=DATABASE_URL; output -->
```bash
cat billing.env
```

```text
# Configuration of the billing service (example values, not real credentials)
DATABASE_URL=postgresql://billing:example-password-change-me@db:5432/billing
CURRENCY=EUR
```

<!-- test -->
```bash
docker rm billing > /dev/null
docker run -d --name billing -p 8080:8080 --env-file billing.env -v "$(pwd):/app" -w /app python:3.14-slim python app.py > /dev/null
```

## Verification

<!-- test: retry=10; contains=billing ok; output -->
```bash
curl -s http://localhost:8080
docker logs billing
```

```text
billing ok, currency EUR
billing: starting with database db:5432/billing
172.17.0.1 - - [05/Oct/2026 10:23:47] "GET / HTTP/1.1" 200 -
```

The log prints only the host part of the URL, never the password: keep secrets out of logs.

## Prevention

- Fail at start-up with a clear message when a required variable is missing (as `app.py` does), never later.
- Document every variable in a committed `.env.example`; keep the real `.env` out of Git and out of the image
  (`.gitignore`, `.dockerignore`, lessons 037, 061).
- In Compose, `${DATABASE_URL:?DATABASE_URL is required}` stops `docker compose up` before anything starts
  (lesson 067).
- Real secrets belong in a secret store or Docker/Compose secrets, not in plain variables (lesson 061).

## Cleanup

<!-- test -->
```bash
docker rm -f billing > /dev/null
rm -rf ~/docker-practice/trouble-11
```

Next: [Problem 12 · Permission denied](../12-permission-denied/README.md)
