<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 061 · Configuration vs secrets · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate is asked for the container configuration to debug a problem, and pastes `docker inspect` output into a
ticket:

```bash
docker inspect db-env --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
```

```text
POSTGRES_PASSWORD=example-db-password-change-me
```

The password is now in the ticket system.

## Troubleshoot it

An environment variable is part of the container's configuration, so everything that reads configuration sees it:
`docker inspect`, anyone in the `docker` group, monitoring agents, and every process inside the container:

```bash
docker exec db-env sh -c 'env | grep POSTGRES_PASSWORD'
```

```text
POSTGRES_PASSWORD=example-db-password-change-me
```

The secret-file container exposes only the path:

```bash
docker inspect db-file --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
```

```text
POSTGRES_PASSWORD_FILE=/run/secrets/db_password
```

## Fix it

Recreate the leaky container with the secret file, then **rotate** the leaked password (it must be considered known):

```bash
docker rm -f db-env > /dev/null
docker run -d --name db-env \
  -v "$(pwd)/db_password.txt:/run/secrets/db_password:ro" \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/db_password postgres:18-alpine > /dev/null
docker inspect db-env | grep -q 'change-me' || echo "no password in inspect"
```

For applications you write yourself, follow the same convention: read `DB_PASSWORD_FILE` if it is set, otherwise
`DB_PASSWORD`. Docker Compose (`secrets:`, lesson 067) and Kubernetes (Secrets mounted as files) build on this pattern.
