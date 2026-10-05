# Troubleshooting problem 15 · Data disappeared

> ⏱ 20 minutes · run every command from the course folder · related lessons: 053, 055, 056, 058

## Problem

A PostgreSQL container ran for weeks. It was recreated for a configuration change, and the application now reports
`relation "orders" does not exist`: the whole database is empty. Nobody deleted anything.

## Symptoms

Reproduce it: a database started **without** a volume option, with one order in it.

<!-- test -->
```bash
docker run -d --name db -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
```

<!-- test: retry=30; contains=accepting connections -->
```bash
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

<!-- test: contains=INSERT; output -->
```bash
docker exec db psql -U postgres -c "create table orders (id int, item text)" -c "insert into orders values (1, 'espresso beans')"
```

```text
CREATE TABLE
INSERT 0 1
```

The container is recreated (the same `docker run`, as any update does):

<!-- test -->
```bash
docker rm -f db > /dev/null
docker run -d --name db -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
```

<!-- test: retry=30; contains=accepting connections -->
```bash
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

<!-- test: fail; contains=does not exist; output -->
```bash
docker exec db psql -U postgres -c "select * from orders" 2>&1
```

```text
ERROR:  relation "orders" does not exist
LINE 1: select * from orders
                      ^
```

## Investigation

**1. Does the image declare a data volume?**

<!-- test: contains=/var/lib/postgresql; output -->
```bash
docker image inspect --format '{{json .Config.Volumes}}' postgres:18-alpine
```

```text
{"/var/lib/postgresql":{}}
```

**2. What is mounted there now?**

<!-- test: contains=/var/lib/postgresql; output -->
```bash
docker inspect --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}' db
```

```text
volume 6c5e86f1babf5027047611781247687f55a3ebd6a72161e9309b3735bfd9746c -> /var/lib/postgresql
```

A volume with a random 64-character name: an **anonymous volume**, created new for this container.

**3. Is the old one still there?** Volumes are not deleted with their container (unless `docker rm -v` or `--rm`):

<!-- test: contains=volumes not used by any container: 1; output -->
```bash
docker volume ls --filter dangling=true --format '{{.Name}}' | cut -c1-12
echo "volumes not used by any container: $(docker volume ls -q --filter dangling=true | wc -l)"
```

```text
5fd1edc7b7e3
volumes not used by any container: 1
```

## Commands

| Command | What it tells you |
|---|---|
| `docker image inspect --format '{{json .Config.Volumes}}' IMAGE` | paths the image stores data in (`VOLUME`) |
| `docker inspect --format '{{range .Mounts}}…{{end}}' NAME` | anonymous (random name) or named volume, and where |
| `docker volume ls --filter dangling=true` | volumes no container uses: candidates for lost data |
| `docker volume inspect VOL` | its creation date, to identify the right one |

## Output interpretation

The `postgres` image declares `VOLUME /var/lib/postgresql`. Without `-v`, Docker creates an **anonymous** volume for
it, and every new container gets a **new** one. The data was never lost: it sits in the old, now unused volume. A
`docker volume prune -a`, a `docker compose down -v` or `docker run --rm` would have deleted it for good.

## Root cause

The database was run without a named volume. Recreating the container attached a fresh anonymous volume, so the
database started empty.

## Fix

Recover the data first: copy the old anonymous volume into a **named** volume, then run the database with that name.

<!-- test: contains=copied; output -->
```bash
old=$(docker volume ls -q --filter dangling=true)
docker volume create pgdata > /dev/null
docker run --rm -v "$old":/from -v pgdata:/to alpine:3.23 cp -a /from/. /to/
echo "copied $(echo "$old" | cut -c1-12)… into pgdata"
```

```text
copied 5fd1edc7b7e3… into pgdata
```

<!-- test -->
```bash
docker rm -f -v db > /dev/null
docker run -d --name db -v pgdata:/var/lib/postgresql \
  -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
```

<!-- test: retry=30; contains=accepting connections -->
```bash
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

## Verification

The order is back, and it survives the next recreation:

<!-- test: contains=espresso beans; output -->
```bash
docker exec db psql -U postgres -tAc "select item from orders"
```

```text
espresso beans
```

<!-- test -->
```bash
docker rm -f db > /dev/null
docker run -d --name db -v pgdata:/var/lib/postgresql \
  -e POSTGRES_PASSWORD=example-password-change-me postgres:18-alpine > /dev/null
```

<!-- test: retry=30; contains=espresso beans; output -->
```bash
docker exec db psql -U postgres -tAc "select item from orders"
```

```text
espresso beans
```

## Prevention

- Every stateful container gets a **named** volume (or a bind mount) for its data path: `-v pgdata:/var/lib/postgresql`
  or `volumes: [pgdata:/var/lib/postgresql]` in Compose (lessons 058, 066).
- Read the image's `VOLUME` paths (and its documentation: PostgreSQL 18 images use `/var/lib/postgresql`, older ones
  `/var/lib/postgresql/data`).
- Be careful with `docker volume prune`, `docker compose down -v` and `--rm` on databases.
- Volumes are not backups: back up with `pg_dump` and test the restore.

## Cleanup

<!-- test -->
```bash
docker rm -f db > /dev/null
docker volume rm pgdata > /dev/null
docker volume prune -af > /dev/null
```

> `docker volume prune -af` removes **every** unused volume on this engine; on a computer with other projects, remove
> the anonymous volumes of this exercise by name instead.

Next: [Problem 16 · Build failure](../16-build-failure/README.md)
