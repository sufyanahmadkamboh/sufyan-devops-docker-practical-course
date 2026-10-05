# Lesson 067 · Environment variables in Compose

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Compose uses environment variables in two different places, and mixing them up is a classic source of confusion:

1. **Interpolation**: `${VAR}` inside `compose.yaml` is replaced by Compose itself, from your shell or from a `.env`
   file next to `compose.yaml`. It configures the file (ports, image tags, defaults).
2. **Container environment**: `environment:` and `env_file:` set variables **inside** the container, for the application.

## Visual

```text
 shell variables ──┐  (shell wins over .env)
 .env file ────────┴─▶ Compose replaces ${API_PORT}, ${GREETING:-default} in compose.yaml
                                     │
                                     ▼
                        resolved file (docker compose config)
                                     │
               environment: + env_file: api.env
                                     │
                                     ▼
                     container api: REDIS_HOST, GREETING, APP_VERSION, LOG_LEVEL

 ${VAR}            empty string if unset (+ a warning)
 ${VAR:-default}   default if unset or empty
 ${VAR:?message}   stop with an error if unset or empty
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-067 examples/python-api
cp -r 10-compose/067-compose-environment/examples/. ~/docker-practice/lesson-067/
cd ~/docker-practice/lesson-067
cp .env.example .env
cat compose.yaml .env api.env
```

Projects commit a `.env.example` and each developer copies it to `.env`, which is listed in `.gitignore`: the real
`.env` may hold machine-specific values or credentials.

## Demonstration

See what interpolation produced, before anything runs:

<!-- test: contains=published: "8080"; output -->
```bash
docker compose config | grep -E 'GREETING|APP_VERSION|published'
```

```text
      APP_VERSION: 1.4.0
      GREETING: Hello from the .env file
        published: "8080"
```

`API_PORT` and `GREETING` came from `.env`; `APP_VERSION` from `api.env`. A shell variable wins over `.env`:

<!-- test: contains=from the shell; output -->
```bash
GREETING="Hello from the shell" docker compose config | grep GREETING
```

```text
      GREETING: Hello from the shell
```

Start the stack and look inside the container:

<!-- test: contains=LOG_LEVEL=info; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose exec api sh -c 'env | grep -E "^(GREETING|REDIS_HOST|APP_VERSION|LOG_LEVEL)=" | sort'
```

```text
APP_VERSION=1.4.0
GREETING=Hello from the .env file
LOG_LEVEL=info
REDIS_HOST=redis
```

`API_PORT` is not in the container: it only configured the file.

## Command breakdown

| Syntax / command | Meaning |
|---|---|
| `${VAR}`, `${VAR:-default}`, `${VAR:?error}` | interpolation in `compose.yaml` |
| `.env` (next to `compose.yaml`) | values for interpolation; not passed to containers |
| `environment:` | variables inside the container |
| `env_file: [file]` | variables inside the container, from a file |
| `docker compose config` | the file after interpolation: check values here first |
| `--env-file FILE` | use another file instead of `.env` (for example `.env.staging`) |

## Hands-on lab

**Instructions.** Start the API on port 8090 instead of 8080 without editing any file, and check the greeting on `/`.

**Expected result.** `curl localhost:8090/` answers with `Hello from the .env file`.

**Verification.**

<!-- test: retry=15; contains=Hello from the .env file -->
```bash
cd ~/docker-practice/lesson-067
API_PORT=8090 docker compose up -d 2> /dev/null
curl -s localhost:8090/
```

Back to the `.env` value for the next steps:

<!-- test -->
```bash
docker compose up -d 2> /dev/null
```

## Break it

A teammate clones the repository and runs the stack. `.env` is not in Git, so they do not have it:

<!-- test: contains=not set; output -->
```bash
mv .env .env.disabled
docker compose up -d 2>&1 | grep -i warn | head -1
```

```text
time="2026-10-05T19:12:36+02:00" level=warning msg="The \"API_PORT\" variable is not set. Defaulting to a blank string."
```

<!-- test: fail; contains=HTTP 000; output -->
```bash
curl -s -w '\nHTTP %{http_code}\n' localhost:8080/ | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
HTTP 000
```

## Troubleshoot it

Compose printed a warning, not an error, and started the stack anyway. With `API_PORT` empty, `":5000"` means "publish
container port 5000 on a **random** host port". Ask Compose where it went:

<!-- test: contains=0.0.0.0; output -->
```bash
docker compose config | grep -A 3 'ports:'
docker compose port api 5000
```

```text
time="2026-10-05T19:12:37+02:00" level=warning msg="The \"API_PORT\" variable is not set. Defaulting to a blank string."
    ports:
      - mode: ingress
        target: 5000
        protocol: tcp
time="2026-10-05T19:12:37+02:00" level=warning msg="The \"API_PORT\" variable is not set. Defaulting to a blank string."
0.0.0.0:50812
```

No `published:` line, and a random port. The greeting also fell back to its default (`Hello from Compose`).

## Fix it

Restore the `.env` file, and make the file fail loudly instead of silently when a required value is missing:

<!-- test: fail; contains=API_PORT must be set; output -->
```bash
sed -i.bak 's/"${API_PORT}:5000"/"${API_PORT:?API_PORT must be set, copy .env.example to .env}:5000"/' compose.yaml && rm compose.yaml.bak
docker compose config 2>&1 > /dev/null
```

```text
error while interpolating services.api.ports.[]: required variable API_PORT is missing a value: API_PORT must be set, copy .env.example to .env
```

<!-- test: retry=15; contains=Hello from the .env file -->
```bash
mv .env.disabled .env
docker compose up -d 2> /dev/null
curl -s localhost:8080/
```

## Practice challenge

Create `.env.staging` with `API_PORT=8085` and `GREETING=Hello from staging`, and start the stack with it, without
changing `.env`.

<details>
<summary>Solution</summary>

<!-- test: retry=15; contains=Hello from staging; output -->
```bash
cd ~/docker-practice/lesson-067
printf 'API_PORT=8085\nGREETING=Hello from staging\n' > .env.staging
docker compose --env-file .env.staging up -d 2> /dev/null
curl -s localhost:8085/
```

```text
{"hostname":"7741779652cd","message":"Hello from staging"}
```

`--env-file` replaces `.env` for interpolation; one `compose.yaml` serves several environments.

</details>

## Real-world example

A repository ships `compose.yaml` and `.env.example`. Developers copy the example and adjust ports that clash on their
machine; CI writes its own `.env` from pipeline variables. Required values use `${VAR:?message}`, so a missing setting
stops the deployment with a clear message instead of starting a half-configured service. Real secrets do not belong in
any of these files: lesson 061 and the security module cover secrets.

## Recap

- `${VAR}` in `compose.yaml` is interpolation: from the shell, then `.env`. `docker compose config` shows the result.
- `environment:` and `env_file:` set variables inside containers.
- An unset `${VAR}` is only a warning: use `${VAR:-default}` or `${VAR:?message}`.
- Commit `.env.example`, never `.env`.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-067
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-067
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 068 · depends_on vs readiness](../068-depends-on-vs-readiness/README.md)
