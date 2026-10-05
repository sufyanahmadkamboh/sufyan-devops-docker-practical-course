# Troubleshooting problem 10 · Database connection failure

> ⏱ 20 minutes · run every command from the course folder · related lessons: 049, 058, 059

## Problem

The API was moved into a container next to its PostgreSQL container. It worked on the laptop, where PostgreSQL ran
locally; in the container it cannot connect: `Connection refused`, although the database container is running.

## Symptoms

Reproduce it. The database:

<!-- test -->
```bash
docker network create shop > /dev/null
docker run -d --name db --network shop \
  -e POSTGRES_PASSWORD=example-password-change-me -e POSTGRES_DB=shop postgres:18-alpine > /dev/null
```

Wait until PostgreSQL accepts TCP connections (`pg_isready` asks the server, lesson 068):

<!-- test: retry=30; contains=accepting connections -->
```bash
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

The client, configured as on the laptop (`PGHOST=localhost`). The `postgres` image includes the `psql` client, so it
plays the API:

<!-- test: fail; contains=Connection refused; output -->
```bash
docker run --rm --network shop -e PGHOST=localhost -e PGUSER=postgres -e PGDATABASE=shop \
  -e PGPASSWORD=example-password-change-me postgres:18-alpine psql -c 'select 1' 2>&1
```

```text
psql: error: connection to server at "localhost" (::1), port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
	Is the server running on that host and accepting TCP/IP connections?
```

## Investigation

**1. Is the database up and listening?**

<!-- test: contains=accepting connections; output -->
```bash
docker ps --filter name=db --format '{{.Names}}: {{.Status}}'
docker exec db pg_isready -h 127.0.0.1 -U postgres
```

```text
db: Up 3 seconds
127.0.0.1:5432 - accepting connections
```

**2. Where did the client try to connect?** The error names it: `localhost (::1), port 5432` and `localhost
(127.0.0.1)`. Inside a container, `localhost` is **that container**, and nothing listens on 5432 in the client
container.

**3. What is the database's name on the network?**

<!-- test: contains=db; output -->
```bash
docker network inspect shop --format '{{range .Containers}}{{.Name}} {{end}}'
docker run --rm --network shop busybox:1.37 nslookup db 2>&1 | grep -A1 'Name:'
```

```text
db 
Name:	db
Address: 172.18.0.2
```

## Commands

| Command | What it tells you |
|---|---|
| `docker exec DB pg_isready -h 127.0.0.1` | the server is up and accepts TCP connections |
| `docker network inspect NET` | which containers can reach each other, by name |
| `docker run --rm --network NET busybox:1.37 nslookup NAME` | whether a name resolves on that network |
| `docker logs DB` | authentication failures and startup errors, seen from the server |

## Output interpretation

The database client's message tells you which layer failed:

| Message | Layer | Typical cause |
|---|---|---|
| `Connection refused` | TCP: nothing listens there | `localhost` in a container, wrong port, DB still starting |
| `could not translate host name "x"` | DNS | typo, or not on the same network ([problem 08](../08-wrong-network/README.md)) |
| `timeout expired` | network path | firewall, unroutable address |
| `password authentication failed` | the server answered | wrong user/password |
| `database "x" does not exist` | the server answered | wrong database name, or the volume was initialized earlier |

See the last two layers for yourself:

<!-- test: fail; contains=password authentication failed; output -->
```bash
docker run --rm --network shop -e PGHOST=db -e PGUSER=postgres -e PGDATABASE=shop \
  -e PGPASSWORD=wrong-password postgres:18-alpine psql -c 'select 1' 2>&1
```

```text
psql: error: connection to server at "db" (172.18.0.2), port 5432 failed: FATAL:  password authentication failed for user "postgres"
```

## Root cause

The connection setting `PGHOST=localhost` was copied from the laptop. In a container it points to the client itself;
the database is another container, reachable by its name `db` on the shared network.

## Fix

Configure the host by **service name**, through the environment (lesson 059):

<!-- test: contains=connected to shop; output -->
```bash
docker run --rm --network shop -e PGHOST=db -e PGUSER=postgres -e PGDATABASE=shop \
  -e PGPASSWORD=example-password-change-me postgres:18-alpine psql -tAc "select 'connected to ' || current_database()"
```

```text
connected to shop
```

## Verification

The server log shows the authentication failure and nothing for the refused connections, which never reached it:

<!-- test: contains=password authentication failed; output -->
```bash
docker logs db 2>&1 | grep -m1 'password authentication failed'
```

```text
2026-10-05 10:23:38.989 UTC [93] FATAL:  password authentication failed for user "postgres"
```

## Prevention

- Never hard-code `localhost` for another service: read `DB_HOST` (or a `DATABASE_URL`) from the environment.
- Wait for readiness, not for "container started": a healthcheck with `pg_isready` and
  `depends_on: condition: service_healthy` in Compose (lessons 068, 069).
- Make the application retry its first connection for a while; databases restart.

## Cleanup

<!-- test -->
```bash
docker rm -f db > /dev/null
docker network rm shop > /dev/null
```

Next: [Problem 11 · Missing environment variable](../11-missing-environment-variable/README.md)
