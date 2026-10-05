<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 058 · A persistent database · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Many older tutorials mount the volume at `/var/lib/postgresql/data` (the path of Postgres 17 and earlier images).
Run a second database that way:

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
