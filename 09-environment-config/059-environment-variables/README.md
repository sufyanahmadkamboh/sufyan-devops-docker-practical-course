# Lesson 059 · Environment variables

> Level 10 · Environment configuration · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

The same image must run in development, staging and production with different settings: ports, URLs, feature flags,
log levels. The standard way to hand those settings to a container is **environment variables**, set with `-e` when
the container is created. The image can define defaults (`ENV` in the Dockerfile, lesson 030); `-e` overrides them.
Build once, configure per environment: that is the twelve-factor rule "store config in the environment".

## Visual

```text
                 one image: node-api:1.0
                          │
      ┌───────────────────┼─────────────────────┐
      ▼                   ▼                     ▼
  development          staging              production
  -e GREETING=dev      -e GREETING=Hi        -e GREETING=Welcome
  -e APP_VERSION=dev   -e APP_VERSION=1.4.0  -e APP_VERSION=1.4.0

  inside the container: process.env.GREETING / os.environ["GREETING"] / $GREETING

  precedence:  -e on docker run  >  ENV in the image  >  the application's own default
```

## Lab setup

The Node.js API of the course reads `PORT`, `GREETING` and `APP_VERSION` from its environment:

<!-- test: contains=GREETING -->
```bash
bash scripts/lab.sh lesson-059 examples/node-api
cd ~/docker-practice/lesson-059
grep -n 'process.env' server.js
```

## Demonstration

Every container already has some variables, from Docker (`HOSTNAME`) and from the image (`PATH`, `NODE_VERSION`):

<!-- test: contains=NODE_VERSION; output -->
```bash
docker run --rm node:24-alpine env | sort
```

```text
HOME=/root
HOSTNAME=e09a1fa8d8f4
NODE_VERSION=24.21.0
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PWD=/
SHLVL=1
YARN_VERSION=1.22.22
```

Run the API with no configuration, then with configuration:

<!-- test: contains=Hello from Node.js; contains=Welcome to the cafe; output; retry=5 -->
```bash
docker run -d --name default-api -p 8080:3000 -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
docker run -d --name configured-api -p 8081:3000 -v "$(pwd):/app:ro" -w /app \
  -e GREETING="Welcome to the cafe" -e APP_VERSION=1.4.0 node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8080; echo
curl -s http://localhost:8081; echo
```

```text
{"message":"Hello from Node.js","hostname":"5baa913df7e7","version":"dev"}
{"message":"Welcome to the cafe","hostname":"eaeb4c535274","version":"1.4.0"}
```

Same code, same image, different behaviour. `-e NAME` without a value copies the variable from your shell:

<!-- test: contains=table 12; output -->
```bash
export TABLE=12
docker run --rm -e TABLE alpine:3.23 sh -c 'echo "table $TABLE"'
```

```text
table 12
```

## Command breakdown

| Form | Meaning |
|---|---|
| `-e NAME=value` | set a variable in the container |
| `-e NAME` | copy NAME's value from the shell that runs `docker` (unset there → not set in the container) |
| `--env NAME=value` | the long form of `-e` |
| `docker inspect C --format '{{json .Config.Env}}'` | every variable the container was created with |
| `ENV NAME=value` (Dockerfile) | a default baked into the image (lesson 030) |

## Hands-on lab

**Instructions.** Show the complete environment the `configured-api` container was created with, and change the port
the application listens on **inside** its container to `4000` in a new container `port-api`, published on host port
8082.

**Expected result.** `GREETING=Welcome to the cafe` in the list; `port-api` answers on 8082 and logs
`listening on port 4000`.

**Verification.**

<!-- test: contains=GREETING=Welcome to the cafe; contains=listening on port 4000; retry=5 -->
```bash
docker inspect configured-api --format '{{range .Config.Env}}{{println .}}{{end}}'
docker run -d --name port-api -p 8082:4000 -e PORT=4000 -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8082 > /dev/null && docker logs port-api
```

## Break it

Start a database without its required configuration:

<!-- test: contains=Exited (1); output; retry=5 -->
```bash
docker run -d --name db postgres:18-alpine > /dev/null
sleep 2
docker ps -a --filter name=db --format '{{.Names}}: {{.Status}}'
```

```text
db: Exited (1) 2 seconds ago
```

## Troubleshoot it

The container exited with status 1 a moment after starting. A container that exits immediately has written the
reason to its log:

<!-- test: contains=superuser password is not specified; output=head:3 -->
```bash
docker logs db 2>&1
```

```text
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the
       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".
...
```

The Postgres image refuses to create a database without a password for the `postgres` superuser. Images document
their variables (on their Docker Hub page); required ones make the container fail fast when missing, which is far
better than starting with an insecure default.

## Fix it

Recreate the container with the variable (a container's environment cannot be changed after it was created):

<!-- test: contains=accepting connections; output; retry=15 -->
```bash
docker rm db > /dev/null
docker run -d --name db -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
sleep 3
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

```text
127.0.0.1:5432 - accepting connections
```

A password on the command line ends up in your shell history and in `docker inspect`. Lesson 060 moves it into a
file, lesson 061 handles it as a secret.

## Practice challenge

Without changing any file, run the API for three "environments" at once (ports 8083, 8084, 8085), each with its own
`GREETING` and `APP_VERSION`, and show the three answers.

<details>
<summary>Solution</summary>

<!-- test: contains=dev; contains=staging; contains=production; output; retry=5 -->
```bash
port=8083
for envname in dev staging production; do
  docker run -d --name "api-$envname" -p "$port:3000" -v "$(pwd):/app:ro" -w /app \
    -e GREETING="Hello from $envname" -e APP_VERSION="1.4.0-$envname" node:24-alpine node server.js > /dev/null
  port=$((port + 1))
done
sleep 1
for port in 8083 8084 8085; do curl -s "http://localhost:$port"; echo; done
```

```text
{"message":"Hello from dev","hostname":"b955ad0fe2e5","version":"1.4.0-dev"}
{"message":"Hello from staging","hostname":"91764306e159","version":"1.4.0-staging"}
{"message":"Hello from production","hostname":"aa600a151131","version":"1.4.0-production"}
```

One artefact, three configurations: exactly how the same image moves from development to production.

</details>

## Real-world example

A team's CI builds `orders-api:1.4.0` once. The staging deployment sets `DATABASE_HOST=staging-db`,
`LOG_LEVEL=debug`; production sets `DATABASE_HOST=prod-db`, `LOG_LEVEL=info`. When production shows a bug, they run
the exact same image locally with production-like variables to reproduce it, because nothing environment-specific is
baked into the image.

## Recap

- Configuration goes into the container as environment variables: `-e NAME=value`, or `-e NAME` from the shell.
- `-e` overrides `ENV` defaults of the image; a container's environment is fixed when it is created.
- A container that exits immediately often lacks a required variable: `docker logs` tells you which.
- Passwords in `-e` are visible in `docker inspect` and shell history (lessons 060, 061).

## Cleanup

<!-- test -->
```bash
docker rm -f default-api configured-api port-api db api-dev api-staging api-production > /dev/null
rm -rf ~/docker-practice/lesson-059
```

Next: [Lesson 060 · Environment files](../060-env-files/README.md)
