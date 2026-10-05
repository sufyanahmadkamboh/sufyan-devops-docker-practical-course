# Lesson 068 · depends_on vs readiness

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

`depends_on: [db]` only controls the **start order**: Compose starts `db`'s container first, then the dependent service.
It does not wait until the database inside is **ready** to accept connections. A database needs seconds to initialise;
an application that connects immediately fails. The fix is to define what "ready" means (a **healthcheck**) and wait
for it: `condition: service_healthy`.

## Visual

```text
 time ─────────────────────────────────────────────────────────────────────────▶

 db container        started ──── initialising (initdb, restart) ──── ready: accepts connections
                        │                                                    │
 depends_on: [db]       └─▶ migrate starts here → psql → Connection refused ✗
                                                                             │
 condition:                                                                  └─▶ migrate starts here → ✓
   service_healthy      (healthcheck: pg_isready … every 2 s, until it passes)
```

| `condition:` | Waits until the dependency … |
|---|---|
| `service_started` (what `depends_on: [db]` means) | has a running container |
| `service_healthy` | reports `healthy` (its healthcheck passes) |
| `service_completed_successfully` | has exited with status 0 (for one-off jobs) |

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-068 10-compose/068-depends-on-vs-readiness/examples
cd ~/docker-practice/lesson-068
cat compose.yaml
```

A PostgreSQL database and `migrate`, a one-off job that connects to it once and exits (it stands in for a schema
migration, which every real application runs before it starts).

## Demonstration

"Running" is not "ready". Start only the database and ask PostgreSQL immediately, and again a few seconds later:

<!-- test: contains=accepting connections; output -->
```bash
docker compose up -d db 2> /dev/null
docker compose exec db pg_isready -h 127.0.0.1 || true
sleep 6
docker compose exec db pg_isready -h 127.0.0.1
```

```text
127.0.0.1:5432 - no response
127.0.0.1:5432 - accepting connections
```

The container was `running` from the first second; PostgreSQL accepted connections only seconds later. The first start
of a database is the slowest, because it creates its data files first.

<!-- test -->
```bash
docker compose down -v 2> /dev/null
```

## Command breakdown

| Command / key | What it does |
|---|---|
| `depends_on: [db]` | start `db` before this service (order only) |
| `depends_on: {db: {condition: service_healthy}}` | wait until `db` is healthy |
| `healthcheck: test: [...]` | the command Docker runs to decide whether the service is healthy (lesson 069) |
| `pg_isready -h 127.0.0.1` | PostgreSQL's own readiness check (exit 0 = accepting connections) |
| `docker compose up` (without `-d`) | run in the foreground, showing every service's output |

## Hands-on lab

**Instructions.** Start the whole stack (both services) with `docker compose up -d`, wait a few seconds, and look at
the state and exit code of `migrate`.

**Expected result.** `migrate` has `exited` with a non-zero code (2): it ran before the database was ready.

**Verification.**

<!-- test: contains=Exited (2) -->
```bash
cd ~/docker-practice/lesson-068
docker compose up -d 2> /dev/null
sleep 5
docker compose ps -a --format '{{.Service}}: {{.Status}}'
```

## Break it

This is the failure the lab showed, as your team would see it: the job's output.

<!-- test: contains=Connection refused; output -->
```bash
docker compose logs --no-log-prefix migrate
```

```text
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
```

## Troubleshoot it

`Connection refused` on the right host name and port: `db` resolved and the network path exists, but nothing was
listening on port 5432 yet. Compare the start times of the two containers with the time the database became ready:

<!-- test: contains=ready to accept connections; output -->
```bash
docker inspect lesson-068-db-1 lesson-068-migrate-1 --format '{{.Name}} started {{.State.StartedAt}}'
docker compose logs --no-log-prefix -t db | grep "ready to accept connections" | tail -1
```

```text
/lesson-068-db-1 started 2026-10-05T17:12:53.414006527Z
/lesson-068-migrate-1 started 2026-10-05T17:12:53.692126192Z
2026-10-05T17:12:55.501114361Z 2026-10-05 17:12:55.500 UTC [1] LOG:  database system is ready to accept connections
```

`migrate` started half a second after `db`, the database was ready seconds later. `depends_on` did exactly what it
promises: start order, nothing more. On a fast machine the race may sometimes pass, which makes it worse: a flaky
start that fails on the CI server or after a reboot.

## Fix it

Define readiness with a healthcheck and wait for it (`fixed/compose.yaml`):

<!-- test: contains=service_healthy; output -->
```bash
docker compose down -v 2> /dev/null
diff compose.yaml fixed/compose.yaml | grep '^>'
```

```text
>     healthcheck:               # "ready" = PostgreSQL accepts connections
>       test: ["CMD", "pg_isready", "-U", "postgres", "-h", "127.0.0.1"]
>       interval: 2s
>       timeout: 3s
>       retries: 15
>   migrate:
>     depends_on:
>       db:
>         condition: service_healthy   # wait until db's healthcheck passes
```

<!-- test: contains=schema ready; output -->
```bash
cp fixed/compose.yaml compose.yaml
docker compose up -d 2> /dev/null
docker compose ps -a --format '{{.Service}}: {{.Status}}'
docker compose logs --no-log-prefix migrate
```

```text
db: Up 3 seconds (healthy)
migrate: Exited (0) Less than a second ago
    status    
--------------
 schema ready
(1 row)
```

`up -d` itself waited until `db` was healthy before creating `migrate`; the job succeeded on the first try.

## Practice challenge

Add an `api` service (image `alpine:3.23`, command `echo "api starting after the migration"`) that starts only after
`migrate` has **finished successfully**. Show the order in which the three services started.

<details>
<summary>Solution</summary>

<!-- test: contains=api starting after the migration; output -->
```bash
cd ~/docker-practice/lesson-068
cat >> compose.yaml <<'EOF'
  api:
    image: alpine:3.23
    command: echo "api starting after the migration"
    depends_on:
      migrate:
        condition: service_completed_successfully
EOF
docker compose up -d 2> /dev/null
docker compose ps -a --format '{{.CreatedAt}} {{.Service}}' | sort | cut -d' ' -f5
docker compose logs --no-log-prefix api
```

```text
db
migrate
api
api starting after the migration
```

`service_completed_successfully` is made for one-off jobs (migrations, seeding, downloading assets): the application
starts only on a prepared database.

</details>

## Real-world example

A team's integration tests failed about one run in ten in CI: the test runner started while PostgreSQL was still
initialising. Adding a `pg_isready` healthcheck and `condition: service_healthy` removed the flakiness. They also kept
a retry loop in the application's own start-up, because in production the database can restart at any time, and a
healthcheck in Compose does not help there (Kubernetes uses readiness probes for the same idea).

## Recap

- `depends_on` = start order. It does not wait for readiness.
- Readiness needs a definition: a healthcheck (`pg_isready`, an HTTP `/health`, `redis-cli ping`).
- `condition: service_healthy` waits for the healthcheck; `service_completed_successfully` waits for a job.
- Applications should still retry connections: dependencies restart in production too.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-068
docker compose down -v 2> /dev/null
rm -rf ~/docker-practice/lesson-068
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 069 · Healthchecks in Compose](../069-compose-healthchecks/README.md)
