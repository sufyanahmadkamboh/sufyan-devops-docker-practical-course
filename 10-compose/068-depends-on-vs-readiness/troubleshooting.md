<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 068 · depends_on vs readiness · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

This is the failure the lab showed, as your team would see it: the job's output.

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
