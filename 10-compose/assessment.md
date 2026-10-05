# Module 10 assessment · Docker Compose

> Lessons [062](062-why-compose/README.md)–[074](074-compose-up-down/README.md) · ⏱ 45 minutes · try every question
> before opening its answer · run every command from the course folder

## Knowledge check

**1. What does the project name do, and where does it come from by default?**

<details><summary>Answer</summary>

It prefixes every container, network and volume of the project (`lesson-062-api-1`, `lesson-062_default`), so
projects never collide. By default it is the name of the folder that holds `compose.yaml`; `-p NAME` overrides it
(lesson 062).

</details>

**2. How does the `api` service reach the `redis` service, and why does `localhost` not work?**

<details><summary>Answer</summary>

By the service name `redis`, resolved by Docker's DNS on the project network. `localhost` inside a container is the
container itself (lesson 065).

</details>

**3. What is the difference between `${VAR}` in `compose.yaml` and a variable under `environment:`?**

<details><summary>Answer</summary>

`${VAR}` is interpolation: Compose replaces it from the shell or `.env` when it reads the file. `environment:` sets a
variable inside the container for the application (lesson 067).

</details>

**4. `depends_on: [db]` is set, yet the application cannot connect to the database at start. Why, and what is the
fix?**

<details><summary>Answer</summary>

`depends_on` only orders the start; it does not wait until the database accepts connections. Add a healthcheck to `db`
and use `condition: service_healthy` (and keep retries in the application) (lesson 068).

</details>

**5. What does `docker compose down -v` delete that `docker compose down` keeps?**

<details><summary>Answer</summary>

The project's named volumes, and with them the data (lessons 066, 074).

</details>

**6. You changed `app.py`; after `docker compose up -d` the old code still runs. Why?**

<details><summary>Answer</summary>

The image already exists, so Compose does not rebuild it; the code is copied into the image at build time. Use
`docker compose up -d --build` (lesson 073).

</details>

**7. When do you use `docker compose exec`, and when `docker compose run`?**

<details><summary>Answer</summary>

`exec` runs a command in the running container of a service (investigation, administration). `run` creates a new
one-off container from the service's configuration (migrations, scripts); add `--rm` (lesson 072).

</details>

**8. A service is only needed for debugging. How do you keep it in the file without starting it every time?**

<details><summary>Answer</summary>

Give it `profiles: [debug]`; start it with `--profile debug` or `COMPOSE_PROFILES=debug` (lesson 070).

</details>

**9. `docker compose logs worker` is empty although the worker runs. What is the most likely cause?**

<details><summary>Answer</summary>

The process writes its log to a file inside the container instead of stdout/stderr; Docker only captures those
(lesson 071).

</details>

## Practical task

Run the cafe API with Redis so that: the API waits for a healthy Redis, both services have healthchecks, the visit
counter survives `docker compose down`, and `docker compose up --wait` returns only when everything is healthy. Prove
that the counter survives a `down`/`up` cycle.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-10 examples/python-api
cp 10-compose/assessment-files/Dockerfile ~/docker-practice/assessment-10/
cat > ~/docker-practice/assessment-10/compose.yaml <<'EOF'
services:
  api:
    build: .
    ports:
      - "8080:5000"
    environment:
      REDIS_HOST: redis
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)"]
      interval: 5s
      timeout: 3s
      retries: 3
      start_period: 5s
    depends_on:
      redis:
        condition: service_healthy
  redis:
    image: redis:8-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping | grep -q PONG"]
      interval: 2s
      timeout: 2s
      retries: 10

volumes:
  redis-data:
EOF
(cd ~/docker-practice/assessment-10 && docker compose config --quiet) && echo "file valid"
```

<!-- test: contains="visits":3; output -->
```bash
(
  cd ~/docker-practice/assessment-10
  docker compose up -d --build --quiet-build --wait 2> /dev/null
  curl -s localhost:8080/visits > /dev/null; curl -s localhost:8080/visits > /dev/null
  docker compose down 2> /dev/null
  docker compose up -d --wait 2> /dev/null
  curl -s localhost:8080/visits
  docker compose ps --format '{{.Service}}: {{.Status}}'
)
```

```text
{"visits":3}
api: Up 6 seconds (healthy)
redis: Up 8 seconds (healthy)
```

<!-- test -->
```bash
(cd ~/docker-practice/assessment-10 && docker compose down -v --rmi local 2> /dev/null)
rm -rf ~/docker-practice/assessment-10
```

The parentheses run the commands in a **subshell**: its `cd` into the lab folder ends with it, so your terminal stays
in the course folder, ready for the next task.

</details>

## Troubleshooting task

A teammate's stack (`10-compose/assessment-files/broken/compose.yaml`) "worked on their laptop". Set it up from the
course folder, find every problem, fix them, and prove `/visits` works.

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-10-broken examples/python-api
cp 10-compose/assessment-files/Dockerfile 10-compose/assessment-files/broken/compose.yaml ~/docker-practice/assessment-10-broken/
cd ~/docker-practice/assessment-10-broken
```

<details><summary>Solution</summary>

**Problem 1.** Validate the file first:

<!-- test: fail; contains=undefined volume; output -->
```bash
docker compose config 2>&1
```

```text
service "redis" refers to undefined volume cache-data: invalid compose project
```

The named volume is not declared at the top level (lesson 066):

<!-- test: contains=cache-data -->
```bash
printf '\nvolumes:\n  cache-data:\n' >> compose.yaml
docker compose config --volumes
```

**Problem 2.** The stack starts, but `/visits` fails:

<!-- test: contains=Connection refused; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
sleep 3
curl -s -w '\nHTTP %{http_code}\n' localhost:8080/visits | tail -1
docker compose logs api 2>&1 | grep -o "redis.exceptions.ConnectionError.*" | tail -1
```

```text
HTTP 500
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

`localhost` is the API container itself; Redis is the service `redis` (lesson 065):

<!-- test: retry=15; contains=visits; output -->
```bash
sed -i.bak 's/REDIS_HOST: localhost/REDIS_HOST: redis/' compose.yaml && rm compose.yaml.bak
docker compose up -d 2> /dev/null
curl -s localhost:8080/visits
```

```text
{"visits":1}
```

On the laptop, Redis was probably installed locally and the API ran outside a container: there, `localhost` was right.

<!-- test -->
```bash
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/assessment-10-broken
```

</details>

## Real-world scenario

Your team's integration tests in CI fail about once in ten runs with "connection refused" from PostgreSQL, always in the
first test. Locally they always pass. The CI job runs `docker compose up -d` and then the tests. What is happening, and
what do you change?

<details><summary>Model answer</summary>

A start-up race: `up -d` returns when the containers are started, not when PostgreSQL accepts connections. On a busy CI
runner initialisation takes longer than on a laptop, so the first test sometimes runs too early (lesson 068). Add a
`pg_isready` healthcheck to the database service, make the test service (or the API) depend on it with
`condition: service_healthy`, and run `docker compose up -d --wait` in CI so the job continues only when everything is
healthy. Keep connection retries in the application as well: databases restart in production too.

</details>

## Cleanup

Each task above removes its own containers, volumes, images and lab folder.
