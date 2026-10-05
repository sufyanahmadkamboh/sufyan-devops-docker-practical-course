# Lesson 058 · A persistent database

> Level 9 · Storage · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

A database in a container is only as durable as its storage. With a named volume at the right path, you can remove
the container, upgrade the image within the same major version, or move to a new container, and the data stays. With
the wrong path, the database writes into the container (or into an anonymous volume) and the next redeploy starts
empty. This lesson runs Postgres 18 the right way, proves the data survives a new container, and backs it up.

## Visual

```text
  docker run … -v pgdata:/var/lib/postgresql postgres:18-alpine
                     │
                     ▼
  ┌──────────── container db (replaceable) ───────────┐
  │ postgres 18                                        │
  │ PGDATA=/var/lib/postgresql/18/docker  ─────────┐   │
  └────────────────────────────────────────────────┼───┘
                                                   ▼
                         ┌─────────────────────────────────────┐
                         │ volume pgdata (durable)             │
                         │   18/docker/  base/ pg_wal/ …       │
                         └─────────────────────────────────────┘
  docker rm -f db; docker run … -v pgdata:… → "Skipping initialization": the same data
  backup:  docker exec db pg_dump … > backup.sql          restore: psql < backup.sql
```

## Lab setup

The image tells you where it keeps its data, and which path it expects a volume at:

<!-- test: contains=/var/lib/postgresql; output -->
```bash
docker image inspect postgres:18-alpine --format 'VOLUME {{json .Config.Volumes}}{{"\n"}}{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'VOLUME|PGDATA'
mkdir -p ~/docker-practice/lesson-058 && cd ~/docker-practice/lesson-058
printf 'example-db-password-change-me' > db_password.txt
```

```text
VOLUME {"/var/lib/postgresql":{}}
PGDATA=/var/lib/postgresql/18/docker
```

## Demonstration

Start Postgres with a named volume at `/var/lib/postgresql` and the password as a secret file (lesson 061):

<!-- test: contains=accepting connections; retry=20 -->
```bash
docker run -d --name db -v pgdata:/var/lib/postgresql \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password \
  postgres:18-alpine > /dev/null
sleep 3
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

`pg_isready -h 127.0.0.1` checks the TCP listener: during its first start, the image initialises the database with a
temporary server that only listens on a local socket, so a TCP check is the honest "ready" signal. Create some data:

<!-- test: contains=2; output -->
```bash
docker exec db psql -U postgres -c "CREATE TABLE orders (id serial PRIMARY KEY, item text NOT NULL)"
docker exec db psql -U postgres -c "INSERT INTO orders (item) VALUES ('espresso'), ('cappuccino')"
docker exec db psql -U postgres -tAc "SELECT count(*) FROM orders"
```

```text
CREATE TABLE
INSERT 0 2
2
```

Now replace the container completely, as an upgrade or a redeploy does:

<!-- test: contains=accepting connections; retry=20 -->
```bash
docker rm -f db > /dev/null
docker run -d --name db -v pgdata:/var/lib/postgresql \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password \
  postgres:18-alpine > /dev/null
sleep 3
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

<!-- test: contains=espresso; contains=Skipping initialization; output -->
```bash
docker exec db psql -U postgres -tAc "SELECT item FROM orders ORDER BY id"
docker logs db 2>&1 | grep -m1 'Skipping initialization'
```

```text
espresso
cappuccino
PostgreSQL Database directory appears to contain a database; Skipping initialization
```

A brand-new container, the same data: the entrypoint found an existing database in the volume and skipped the
initialisation.

## Command breakdown

| Part | What it does |
|---|---|
| `-v pgdata:/var/lib/postgresql` | the named volume at the path the image declares (`VOLUME`) |
| `PGDATA=/var/lib/postgresql/18/docker` | where Postgres 18 really writes, inside that volume |
| `pg_isready -h 127.0.0.1 -U postgres` | is the server accepting TCP connections? |
| `psql -U postgres -tAc "SQL"` | run one SQL statement; `-tA`: only the values, no table formatting |
| `pg_dump -U postgres DB` | a logical backup (SQL) of one database |

## Hands-on lab

**Instructions.** Find out how much space the database uses in the volume, and which files Postgres created at the top
of its data directory.

**Expected result.** A size of a few tens of megabytes, and entries such as `PG_VERSION`, `base` and `pg_wal`.

**Verification.**

<!-- test: contains=PG_VERSION; contains=base -->
```bash
docker run --rm -v pgdata:/data:ro alpine:3.23 sh -c 'du -sh /data; ls /data/18/docker'
```

## Break it

Many older tutorials mount the volume at `/var/lib/postgresql/data` (the path of Postgres 17 and earlier images).
Run a second database that way:

<!-- test: contains=Exited (1); output; retry=5 -->
```bash
docker run -d --name old-path -v old-pgdata:/var/lib/postgresql/data -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
sleep 5
docker ps -a --filter name=old-path --format '{{.Names}}: {{.Status}}'
```

```text
old-path: Exited (1) 5 seconds ago
```

## Troubleshoot it

The container exited with an error within seconds. Read its log first, then compare its mounts with what the image
declares:

<!-- test: contains=18+; output=head:8 -->
```bash
docker logs old-path 2>&1
```

```text
Error: in 18+, these Docker images are configured to store database data in a
       format which is compatible with "pg_ctlcluster" (specifically, using
       major-version-specific directory names).  This better reflects how
       PostgreSQL itself works, and how upgrades are to be performed.

       See also https://github.com/docker-library/postgres/pull/1259

       Counter to that, there appears to be PostgreSQL data in:
...
```

<!-- test: contains=/var/lib/postgresql/data; output -->
```bash
docker inspect old-path --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{println}}{{end}}'
```

```text
volume old-pgdata -> /var/lib/postgresql/data
volume 0c7718bccfd449ef754884303a8888ce339c436e91b10086e53eecf450f27565 -> /var/lib/postgresql
```

Two mounts: `old-pgdata` at the old path, and an **anonymous** volume at `/var/lib/postgresql`, created because the
image declares that path as its `VOLUME` and nothing was mounted there. Postgres 18 stores its data under
`/var/lib/postgresql/18/docker` and refuses to start when it finds a mount at the old location, so that data cannot
silently end up in the wrong place. (Older images had no such check: a volume at the wrong path meant the database
quietly wrote into an anonymous volume, and the data "disappeared" at the next redeploy.)

## Fix it

<!-- test: contains=accepting connections; retry=20 -->
```bash
docker rm -f old-path > /dev/null
docker volume rm old-pgdata > /dev/null
docker volume prune -f > /dev/null
docker run -d --name old-path -v old-pgdata:/var/lib/postgresql -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
sleep 3
docker exec old-path pg_isready -h 127.0.0.1 -U postgres
```

The rule for every database image: read its documentation (or `docker image inspect … .Config.Volumes`) for the data
path of **that** major version, and mount the volume exactly there.

## Practice challenge

Back up the `orders` table's database with `pg_dump` into `backup.sql` on your computer, delete the table, and restore
it from the backup.

<details>
<summary>Solution</summary>

<!-- test: contains=restored: 2 orders; output -->
```bash
cd ~/docker-practice/lesson-058
docker exec db pg_dump -U postgres postgres > backup.sql
docker exec db psql -U postgres -c "DROP TABLE orders" > /dev/null
docker exec -i db psql -U postgres -q < backup.sql > /dev/null
echo "restored: $(docker exec db psql -U postgres -tAc 'SELECT count(*) FROM orders') orders"
```

```text
restored: 2 orders
```

`docker exec -i` passes your terminal's input (here the file) into the container. A volume protects against losing the
container; only backups protect against deleting the data, a broken disk or a bad migration.

</details>

## Real-world example

A team runs Postgres in containers for development and for a small internal tool. Their runbook: the volume is at the
image's declared path; a nightly `pg_dump` is copied off the server; every upgrade starts with a fresh dump; and a
quarterly drill restores the dump into a new container to prove the backup works. For production customer data, many
teams use a managed database service instead and keep containers for the stateless parts.

## Recap

- Mount a named volume at the path the image declares (`/var/lib/postgresql` for Postgres 18).
- The container is replaceable; the volume holds the data: a new container skips initialisation.
- Wait for readiness with `pg_isready -h 127.0.0.1`, not just "the container is running".
- Volumes are not backups: `pg_dump` regularly and test the restore.

## Cleanup

<!-- test -->
```bash
docker rm -f db old-path > /dev/null
docker volume rm pgdata old-pgdata > /dev/null
rm -rf ~/docker-practice/lesson-058
```

Next: [Lesson 059 · Environment variables](../../09-environment-config/059-environment-variables/README.md)
