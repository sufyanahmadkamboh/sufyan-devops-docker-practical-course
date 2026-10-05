<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 059 · Environment variables · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Start a database without its required configuration:

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
