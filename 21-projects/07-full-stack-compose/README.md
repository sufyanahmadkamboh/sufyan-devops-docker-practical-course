# Project 07 · Full-stack application with Compose

> ⏱ 1.5 hours · run every command from the course folder

## Goal

Build a complete three-tier application and run it with one command: an Nginx container serving the frontend and
forwarding `/api/` to a Python API, which stores its data in PostgreSQL. Separate networks keep the database
unreachable from the frontend, healthchecks order the start-up, and all configuration lives in one `.env` file.

## Requirements

- [ ] Three services in one `compose.yaml`: `web` (Nginx), `api` (Flask + Gunicorn + psycopg), `db` (PostgreSQL 18)
- [ ] Two networks: `front` (web, api) and `back` (api, db), `back` marked `internal`
- [ ] Healthchecks on all three; each service starts only when the one it needs is **healthy**
- [ ] All settings come from `.env` (copied from `.env.example`); nothing environment-specific in the images
- [ ] Only `web` publishes a port; notes survive `docker compose down` and `up`

## Architecture

```text
                    network front                               network back (internal)
 browser ──▶ :8087 ┌────────────────────────┐  /api/  ┌──────────────────┐        ┌────────────────────┐
                   │ web  nginx:1.30-alpine │ ──────▶ │ api  Flask       │ ─────▶ │ db  postgres:18    │
                   │ index.html, app.js     │         │ gunicorn :8000   │  SQL   │ :5432              │
                   └────────────────────────┘         └──────────────────┘        └─────────┬──────────┘
                                                                                            ▼
 .env ──▶ WEB_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD                     volume db-data
```

## Build it

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-07 21-projects/07-full-stack-compose/solution
cd ~/docker-practice/project-07
cp .env.example .env
find . -type f | sort
```

<!-- test: contains=internal: true; output -->
```bash
cat compose.yaml
```

```text
# A full-stack application: Nginx (static files + reverse proxy) → Python API → PostgreSQL.
#   network front: web, api            network back (internal): api, db
name: project07

services:
  web:
    build: ./web
    image: project07-web:1.0
    ports: ["${WEB_PORT:-8087}:8080"]
    networks: [front]
    depends_on:
      api: { condition: service_healthy }
    restart: unless-stopped

  api:
    build: ./api
    image: project07-api:1.0
    environment:
      DB_HOST: db
      DB_NAME: ${POSTGRES_DB}
      DB_USER: ${POSTGRES_USER}
      DB_PASSWORD: ${POSTGRES_PASSWORD}
    networks: [front, back]
    depends_on:
      db: { condition: service_healthy }
    restart: unless-stopped

  db:
    image: postgres:18-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes: [db-data:/var/lib/postgresql]
    networks: [back]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h 127.0.0.1 -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10
    restart: unless-stopped

networks:
  front: {}
  back:
    internal: true

volumes:
  db-data: {}
```

Check what Compose makes of it with the values from `.env`, then build and start:

<!-- test: contains=8087 -->
```bash
docker compose config --format json | grep -o '"published": *"[0-9]*"'
```

<!-- test: contains=Healthy -->
```bash
docker compose up -d --build --wait 2>&1 | tail -3
```

## Verify

<!-- test: contains=first note; retry=10; output -->
```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"text": "first note"}' http://localhost:8087/api/notes
echo
curl -s http://localhost:8087/api/notes
```

```text
{"id":1,"text":"first note"}

[{"id":1,"text":"first note"}]
```

<!-- test: contains=Cafe notice board -->
```bash
curl -s http://localhost:8087/ | grep "<h1>"
```

All healthy, one published port:

<!-- test: contains=healthy; output -->
```bash
docker compose ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
```

```text
SERVICE   STATUS                    PORTS
api       Up 11 seconds (healthy)   8000/tcp
db        Up 17 seconds (healthy)   5432/tcp
web       Up 6 seconds (healthy)    0.0.0.0:8087->8080/tcp, [::]:8087->8080/tcp
```

The networks: `web` cannot reach the database at all.

<!-- test: contains=back internal=true; output -->
```bash
docker network ls --filter name=project07 --format '{{.Name}} internal={{.Internal}}' | sed 's/project07_//'
docker compose exec web sh -c 'nslookup db > /dev/null 2>&1 && echo "web can resolve db" || echo "web cannot resolve db"'
```

```text
back internal=true
front internal=false
web cannot resolve db
```

Data survives recreating every container:

<!-- test: contains=first note; retry=10 -->
```bash
docker compose down 2>&1 | tail -1
docker compose up -d --wait 2>&1 | tail -1
curl -s http://localhost:8087/api/notes
```

## Break it and fix it

Security asks for a new database password. Someone changes it in `.env` and redeploys:

<!-- test -->
```bash
sed -i.bak 's/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=new-example-password/' .env
docker compose up -d 2>&1 | tail -1
```

<!-- test: contains=password authentication failed; retry=20; output -->
```bash
docker compose logs api --no-log-prefix 2>&1 | grep -m1 "password authentication failed"
```

```text
waiting for the database (attempt 1): connection failed: connection to server at "172.19.0.2", port 5432 failed: FATAL:  password authentication failed for user "notes"
```

The API now uses the new password, but PostgreSQL still has the old one. `POSTGRES_PASSWORD` (like every
`POSTGRES_*` variable) is used **only when the data folder is initialized**, on the first start with an empty volume.
After that, the password lives in the database, in the volume. Change it there, then restart the API:

<!-- test: contains=ALTER ROLE -->
```bash
docker compose exec db psql -U notes -d notes -c "ALTER USER notes PASSWORD 'new-example-password'"
```

<!-- test: contains=first note; retry=15 -->
```bash
docker compose up -d --wait --force-recreate api 2>&1 | tail -1
curl -s http://localhost:8087/api/notes
```

`psql` inside the database container connects over the local socket, which the image trusts; that is why it worked
without the password.

## Stretch goals

- Move the password out of `.env` into a Compose secret file and `POSTGRES_PASSWORD_FILE` (the capstone does this).
- Add `read_only: true` and `tmpfs` to `web` and `api`, and `cap_drop: [ALL]` (module 12).
- Add a `profiles: [tools]` service with `adminer` or `psql` for debugging that does not start by default (lesson 070).

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/project-07
docker compose down -v 2>&1 | tail -1
docker image rm -f project07-web:1.0 project07-api:1.0 > /dev/null
cd ~ && rm -rf ~/docker-practice/project-07
```

Next: [Project 08 · Four stacks behind one proxy](../08-multi-stack/README.md)
