# Project 06 · A database container you can back up

> ⏱ 1 hour · run every command from the course folder

## Goal

Run PostgreSQL in a container the way you can trust with data: the schema and seed data created by init scripts, the
data in a named volume that outlives every container, and a **backup that you have actually restored** into a fresh
database. A backup you never restored is only a hope.

## Requirements

- [ ] `postgres:18-alpine` with its data in the named volume `cafe-pgdata`
- [ ] Init scripts (`initdb/*.sql`) create and fill the `menu` table on the first start
- [ ] The data survives removing and recreating the container
- [ ] `pg_dump` writes a backup into a folder of your computer (bind mount)
- [ ] The backup is restored into a new container with a new, empty volume, and the data is identical

## Architecture

```text
            network project06
 ┌──────────────────────────────┐        ┌──────────────────────────────────┐
 │ cafe-db  postgres:18-alpine  │◀──SQL──│ pg_dump  (a one-off container)   │
 │ /var/lib/postgresql          │        │ /backup ◀── bind mount ./backup  │──▶ ./backup/cafe.dump
 └──────────────┬───────────────┘        └──────────────────────────────────┘          │
                ▼                                                                       │ pg_restore
        volume cafe-pgdata                   ┌──────────────────────────────────┐       │
                                             │ cafe-db-restore                  │◀──────┘
 ./initdb ──▶ /docker-entrypoint-initdb.d    │ volume cafe-pgdata-restore       │
 (first start only)                          └──────────────────────────────────┘
```

## Build it

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-06 21-projects/06-database-container/solution
cd ~/docker-practice/project-06
ls -A . initdb
```

`db.env` configures the server, `client.env` the client tools; both hold an obviously fake example password. Create
the network and the volume, then start the database with the init scripts mounted read-only:

<!-- test -->
```bash
docker network create project06 > /dev/null
docker volume create cafe-pgdata > /dev/null
docker run -d --name cafe-db --network project06 --env-file db.env \
  -v cafe-pgdata:/var/lib/postgresql \
  -v "$(pwd)/initdb:/docker-entrypoint-initdb.d:ro" \
  postgres:18-alpine > /dev/null
```

While the init scripts run, PostgreSQL listens only on a local socket; it accepts TCP connections when it is really
ready. So check over TCP:

<!-- test: contains=accepting connections; retry=30 -->
```bash
docker exec cafe-db pg_isready -h 127.0.0.1 -U cafe -d cafe
```

<!-- test: contains=running /docker-entrypoint-initdb.d/02-seed.sql; output -->
```bash
docker logs cafe-db 2>&1 | grep "docker-entrypoint-initdb.d"
```

```text
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/01-schema.sql
/usr/local/bin/docker-entrypoint.sh: running /docker-entrypoint-initdb.d/02-seed.sql
```

## Verify

<!-- test: contains=flat white; output -->
```bash
docker exec cafe-db psql -U cafe -d cafe -c "SELECT id, item, price FROM menu ORDER BY id"
```

```text
 id |    item    | price 
----+------------+-------
  1 | espresso   |  2.20
  2 | flat white |  3.40
  3 | cortado    |  3.10
(3 rows)
```

**Persistence.** Remove the container completely, start a new one on the same volume, and the data is still there:

<!-- test -->
```bash
docker rm -f cafe-db > /dev/null
docker run -d --name cafe-db --network project06 --env-file db.env -v cafe-pgdata:/var/lib/postgresql postgres:18-alpine > /dev/null
```

<!-- test: contains=3; retry=30 -->
```bash
docker exec cafe-db sh -c 'pg_isready -q -h 127.0.0.1 && psql -U cafe -d cafe -tAc "SELECT count(*) FROM menu"'
```

**Backup.** A one-off container on the same network runs `pg_dump` and writes into `./backup` on your computer:

<!-- test: contains=cafe.dump; retry=5 -->
```bash
mkdir -p backup
docker run --rm --network project06 --env-file client.env -v "$(pwd)/backup:/backup" postgres:18-alpine \
  pg_dump --format=custom --file=/backup/cafe.dump
ls -l backup
```

**Restore** into a brand-new database, with a new volume and no init scripts:

<!-- test -->
```bash
docker run -d --name cafe-db-restore --network project06 --env-file db.env \
  -v cafe-pgdata-restore:/var/lib/postgresql postgres:18-alpine > /dev/null
```

<!-- test: contains=accepting connections; retry=30 -->
```bash
docker exec cafe-db-restore pg_isready -h 127.0.0.1 -U cafe -d cafe
```

<!-- test: contains=identical; output -->
```bash
docker run --rm --network project06 --env-file client.env -e PGHOST=cafe-db-restore -v "$(pwd)/backup:/backup" \
  postgres:18-alpine pg_restore --dbname=cafe /backup/cafe.dump
q="SELECT string_agg(item || '=' || price, ',' ORDER BY id) FROM menu"
original=$(docker exec cafe-db psql -U cafe -d cafe -tAc "$q")
restored=$(docker exec cafe-db-restore psql -U cafe -d cafe -tAc "$q")
echo "original: $original"
echo "restored: $restored"
[ "$original" = "$restored" ] && echo "identical"
```

```text
original: espresso=2.20,flat white=3.40,cortado=3.10
restored: espresso=2.20,flat white=3.40,cortado=3.10
identical
```

## Break it and fix it

The menu gets a new item. Add it to the seed script and restart the database:

<!-- test -->
```bash
echo "INSERT INTO menu (item, price) VALUES ('mocha', 3.80);" >> initdb/02-seed.sql
docker rm -f cafe-db > /dev/null
docker run -d --name cafe-db --network project06 --env-file db.env \
  -v cafe-pgdata:/var/lib/postgresql -v "$(pwd)/initdb:/docker-entrypoint-initdb.d:ro" postgres:18-alpine > /dev/null
```

<!-- test: contains=3; retry=30; output -->
```bash
docker exec cafe-db sh -c 'pg_isready -q -h 127.0.0.1 && psql -U cafe -d cafe -tAc "SELECT count(*) FROM menu"'
```

```text
3
```

Still 3 items: the mocha is missing, and there is no error. The logs explain it:

<!-- test: contains=Skipping initialization; output -->
```bash
docker logs cafe-db 2>&1 | grep -i "skipping"
```

```text
PostgreSQL Database directory appears to contain a database; Skipping initialization
```

Init scripts run **only when the data folder is empty**, that is, on the first start with a new volume. They are a
bootstrap, not a migration tool. Changes to an existing database are applied as migrations, explicitly, and kept in
version control:

<!-- test: contains=mocha -->
```bash
docker exec cafe-db psql -U cafe -d cafe -c "INSERT INTO menu (item, price) VALUES ('mocha', 3.80) ON CONFLICT (item) DO NOTHING"
docker exec cafe-db psql -U cafe -d cafe -tAc "SELECT item FROM menu ORDER BY id"
```

(Real projects use a migration tool such as Flyway, Liquibase or the framework's own, run as a one-off container
before the new application version starts.)

## Stretch goals

- Back up with a plain SQL dump (`--format=plain`) and restore it with `psql -f`; compare the two formats.
- Schedule the backup: a small container that runs `pg_dump` every night, keeping the last seven files.
- Pass the password as a file (`POSTGRES_PASSWORD_FILE`) instead of an environment variable (lesson 061).

## Cleanup

<!-- test -->
```bash
docker rm -f cafe-db cafe-db-restore > /dev/null 2>&1 || true
docker volume rm cafe-pgdata cafe-pgdata-restore > /dev/null
docker network rm project06 > /dev/null
cd ~ && rm -rf ~/docker-practice/project-06
```

Next: [Project 07 · Full-stack application with Compose](../07-full-stack-compose/README.md)
