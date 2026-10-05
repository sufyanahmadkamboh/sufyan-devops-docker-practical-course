# Lesson 061 · Configuration vs secrets

> Level 10 · Environment configuration · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

**Configuration** (a log level, a host name, a feature flag) may be seen by anyone who operates the application.
A **secret** (a password, an API key, a private key) must be seen only by the application. Environment variables are
fine for configuration but leak secrets: they appear in `docker inspect`, in the environment of every process in the
container, and in crash reports that dump the environment. The safer pattern is a **secret file**: mounted
read-only, typically under `/run/secrets/`, and read by the application (many official images support `*_FILE`
variables for exactly this). Never bake either into the image (lesson 083).

## Visual

```text
                       configuration                      secret
 examples              LOG_LEVEL, DB_HOST, PORT          DB password, API token, TLS key
 who may see it        operators, logs, tickets           only the application
 how to pass it        -e / --env-file                    a read-only file: /run/secrets/NAME
 visible in inspect    yes (fine)                         -e: YES ✘      file: only the mount path ✔
 in Git                yes (reviewed)                     never (a secret manager, CI secrets)

  docker run -e POSTGRES_PASSWORD=…            → docker inspect shows the password to anyone with Docker access
  docker run -v ./db_password.txt:/run/secrets/db_password:ro
             -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password   → inspect shows only the file's path
```

## Lab setup

A secret file with an obviously fake password (in real life it comes from a secret manager or a CI secret, never from
Git):

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-061
cd ~/docker-practice/lesson-061
printf 'example-db-password-change-me' > db_password.txt
printf 'db_password.txt\n' > .gitignore
```

## Demonstration

First the common way, a password in an environment variable:

<!-- test: contains=accepting connections; retry=15 -->
```bash
docker run -d --name db-env -e POSTGRES_PASSWORD="$(cat db_password.txt)" postgres:18-alpine > /dev/null
sleep 3
docker exec db-env pg_isready -h 127.0.0.1 -U postgres
```

Now the secret-file way: the file is mounted read-only, and the image is told **where** to read the password:

<!-- test: contains=accepting connections; retry=15 -->
```bash
docker run -d --name db-file \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password \
  postgres:18-alpine > /dev/null
sleep 3
docker exec db-file pg_isready -h 127.0.0.1 -U postgres
```

The password from the file works for a login over the network:

<!-- test: contains=logged in; output; retry=10 -->
```bash
docker exec -e PGPASSWORD="$(cat db_password.txt)" db-file psql -h 127.0.0.1 -U postgres -tAc "select 'logged in'"
```

```text
logged in
```

## Command breakdown

| Part | What it does |
|---|---|
| `-v "$(pwd)/db_password.txt:/run/secrets/db_password:ro"` | the secret as a read-only file inside the container |
| `-e POSTGRES_PASSWORD_FILE=/run/secrets/db_password` | configuration: **where** the secret is (not the secret itself) |
| `pg_isready -h 127.0.0.1` | is the server accepting TCP connections? |
| `psql -h 127.0.0.1 -U postgres` | log in over TCP, which requires the password |

## Hands-on lab

**Instructions.** Show who can read the secret file inside `db-file`, and that the container cannot change it.

**Expected result.** The file is listed under `/run/secrets`; writing to it fails with `Read-only file system`.

**Verification.**

<!-- test: contains=db_password; contains=Read-only file system -->
```bash
docker exec db-file ls -l /run/secrets/
docker exec db-file sh -c 'echo changed > /run/secrets/db_password' 2>&1 || true
```

## Break it

A teammate is asked for the container configuration to debug a problem, and pastes `docker inspect` output into a
ticket:

<!-- test: contains=POSTGRES_PASSWORD=example-db-password-change-me; output -->
```bash
docker inspect db-env --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
```

```text
POSTGRES_PASSWORD=example-db-password-change-me
```

The password is now in the ticket system.

## Troubleshoot it

An environment variable is part of the container's configuration, so everything that reads configuration sees it:
`docker inspect`, anyone in the `docker` group, monitoring agents, and every process inside the container:

<!-- test: contains=POSTGRES_PASSWORD; output -->
```bash
docker exec db-env sh -c 'env | grep POSTGRES_PASSWORD'
```

```text
POSTGRES_PASSWORD=example-db-password-change-me
```

The secret-file container exposes only the path:

<!-- test: contains=POSTGRES_PASSWORD_FILE=/run/secrets/db_password; absent=change-me; output -->
```bash
docker inspect db-file --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
```

```text
POSTGRES_PASSWORD_FILE=/run/secrets/db_password
```

## Fix it

Recreate the leaky container with the secret file, then **rotate** the leaked password (it must be considered known):

<!-- test: contains=no password in inspect; retry=15 -->
```bash
docker rm -f db-env > /dev/null
docker run -d --name db-env \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password postgres:18-alpine > /dev/null
docker inspect db-env | grep -q 'change-me' || echo "no password in inspect"
```

For applications you write yourself, follow the same convention: read `DB_PASSWORD_FILE` if it is set, otherwise
`DB_PASSWORD`. Docker Compose (`secrets:`, lesson 067) and Kubernetes (Secrets mounted as files) build on this pattern.

## Practice challenge

The application needs an API token. Mount it as a secret file into a container and read it from the file in the
container's command, so that neither `docker inspect` nor the command line contains the token.

<details>
<summary>Solution</summary>

<!-- test: contains=token length: 22; contains=inspect clean; output -->
```bash
printf 'example-token-0000-abc' > api_token.txt
docker run -d --name worker -v "$(pwd)/api_token.txt:/run/secrets/api_token:ro" alpine:3.23 \
  sh -c 'TOKEN=$(cat /run/secrets/api_token); echo "token length: ${#TOKEN}"; sleep 300' > /dev/null
sleep 1
docker logs worker
docker inspect worker | grep -q 'example-token' || echo "inspect clean"
```

```text
token length: 22
inspect clean
```

The token is read at runtime inside the container. Logging its length (never the value) is enough to prove it was
loaded.

</details>

## Real-world example

After a security review, a team moves every password out of `docker run -e` and Compose `environment:`. The CI system
writes secrets into files on a tmpfs at deploy time and mounts them read-only under `/run/secrets/`; applications read
`*_FILE` variables. Their incident checklist now includes "rotate any secret that appeared in a log, a ticket or
`docker inspect` output".

## Recap

- Configuration may be visible; secrets must not be. Treat every environment variable as visible.
- `-e` secrets leak through `docker inspect`, process environments and crash dumps.
- Pass secrets as read-only files (`/run/secrets/NAME`) and pass only their path as configuration (`*_FILE`).
- A leaked secret must be rotated, not just removed.

## Cleanup

<!-- test -->
```bash
docker rm -f db-env db-file worker > /dev/null
rm -rf ~/docker-practice/lesson-061
```

Next: [Lesson 062 · Why Docker Compose?](../../10-compose/062-why-compose/README.md)
