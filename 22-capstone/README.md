# Capstone · a production-style container stack

> Final project · ⏱ 3 hours · run every command from the course folder

You build, run, harden, verify, break and ship a complete application: a cafe ordering service with a reverse proxy,
a frontend, an API and a PostgreSQL database. Every technique of the course is used once, on purpose, and every one is
**verified with a command**, not assumed. The finished files are in [app/](app/); the walkthrough builds them up and
checks them one by one.

## Architecture

```text
                       host port 8080 (the only published port)
                                   │
 ┌─────────────────────────────────┼───────────────────────────────────────────────────────────┐
 │ network "edge"                  ▼                                                           │
 │                        ┌──────────────────┐   /        ┌──────────────────┐                 │
 │   browser / curl ────▶ │ proxy            │ ─────────▶ │ frontend         │ static files    │
 │                        │ nginx, non-root  │            │ nginx, non-root  │ (Node.js build) │
 │                        └────────┬─────────┘            └──────────────────┘                 │
 │                                 │ /api/                                                     │
 │                                 ▼                                                           │
 │                        ┌──────────────────┐                                                 │
 │                        │ api              │ Go, distroless, user 65532                      │
 └────────────────────────┤                  ├─────────────────────────────────────────────────┘
 ┌────────────────────────┤                  ├─────────────────────────────────────────────────┐
 │ network "backend"      └────────┬─────────┘                    internal: no route outside   │
 │ (internal)                      ▼                                                           │
 │                        ┌──────────────────┐     volume "pgdata"                             │
 │                        │ db  PostgreSQL 18│ ──▶ /var/lib/postgresql                         │
 │                        └──────────────────┘                                                 │
 └─────────────────────────────────────────────────────────────────────────────────────────────┘
   secret: secrets/db_password.txt → /run/secrets/db_password (api, db)
```

## Requirements and where they are met

| Requirement | Where | Verified in step |
|---|---|---|
| Multi-stage builds | [api/Dockerfile](app/api/Dockerfile) (Go → distroless), [frontend/Dockerfile](app/frontend/Dockerfile) (Node.js → Nginx) | 2 |
| Custom networks | `edge` and an internal `backend` in [compose.yaml](app/compose.yaml) | 6 |
| Environment configuration | [.env.example](app/.env.example) → `.env`; `environment:` per service | 1, 3 |
| Secrets | `secrets:` from a file, read by the API and PostgreSQL as `/run/secrets/db_password` | 1, 5 |
| Healthchecks | every service; `depends_on: condition: service_healthy` | 4 |
| Volumes | named volume `pgdata` | 7 |
| Resource limits | `deploy.resources.limits` (CPU, memory, processes) | 8 |
| Logging | `json-file` with rotation (`max-size`, `max-file`); JSON logs from the API | 8 |
| Security | non-root users, read-only root file systems, `cap_drop: [ALL]`, `no-new-privileges`, no shell in the API | 5 |
| Optimization | distroless API image, layer order for cache, `.dockerignore` | 2 |
| Docker Compose | the whole stack is one [compose.yaml](app/compose.yaml) | 3 |
| Registry | push to a local registry and pull back by digest | 10 |
| CI | [.github/workflows/capstone.yml](../.github/workflows/capstone.yml) builds, tests and pushes to GHCR | 11 |
| Documentation | this walkthrough and the comments in every file | |

## Step 1 · Lab and configuration

<!-- test: contains=created secrets/db_password.txt -->
```bash
bash scripts/lab.sh capstone 22-capstone/app
cd ~/docker-practice/capstone
./make-secret.sh
cp .env.example .env
```

Configuration (`.env`) and the secret (`secrets/db_password.txt`) are separate on purpose: `.env` can be shown to
anyone, the secret cannot. Check that the Compose file is valid and that the password does not appear in the
configuration Compose resolves:

<!-- test: contains=valid; absent=POSTGRES_PASSWORD: -->
```bash
docker compose config --quiet && echo "compose file valid"
docker compose config | grep -E "PASSWORD|db_password" | sed 's/^ *//' | sort -u
```

Only the password **file's path** appears, never its content.

## Step 2 · Build the images

<!-- test: contains=capstone/api -->
```bash
docker compose build --quiet
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' | grep capstone/
```

Compare the API image with the image it was built in:

<!-- test: contains=golang:1.26-alpine; output -->
```bash
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' | grep -E "capstone/api|^golang:1.26-alpine"
```

```text
localhost:5000/capstone/api:1.0.0  21.3MB
golang:1.26-alpine  364MB
```

The Go toolchain, the source code and the module cache stayed in the build stage. The final image is the static
binary on distroless: no shell, no package manager, nothing to attack and nothing to patch except the binary.

## Step 3 · Start the stack

`--wait` returns only when every service with a healthcheck is **healthy**, not merely running:

<!-- test: contains=Healthy -->
```bash
docker compose up -d --wait 2>&1 | tail -4
```

<!-- test: contains=proxy; output -->
```bash
docker compose ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
```

```text
SERVICE    STATUS                    PORTS
api        Up 16 seconds (healthy)   8080/tcp
db         Up 22 seconds (healthy)   5432/tcp
frontend   Up 22 seconds (healthy)   80/tcp, 8080/tcp
proxy      Up 11 seconds (healthy)   0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
```

Only the proxy publishes a port. Use the application through it:

<!-- test: contains="status":"ok"; retry=10 -->
```bash
curl -s http://localhost:8080/api/health
```

<!-- test: contains=flat white; output -->
```bash
curl -s -X POST -H "Content-Type: application/json" -d '{"item": "flat white"}' http://localhost:8080/api/orders
echo
curl -s -X POST -H "Content-Type: application/json" -d '{"item": "cortado"}' http://localhost:8080/api/orders
echo
curl -s http://localhost:8080/api/orders
```

```text
{"id":1,"item":"flat white","created":"2026-10-05T09:54:36.771146Z"}

{"id":2,"item":"cortado","created":"2026-10-05T09:54:36.815706Z"}

[{"id":2,"item":"cortado","created":"2026-10-05T09:54:36.815706Z"},{"id":1,"item":"flat white","created":"2026-10-05T09:54:36.771146Z"}]
```

<!-- test: contains=Cafe orders -->
```bash
curl -s http://localhost:8080/ | grep "<title>"
```

Open <http://localhost:8080> in a browser to use the page.

## Step 4 · Health, not just "running"

<!-- test: contains=healthy; output -->
```bash
for s in proxy frontend api db; do
  echo "$s: $(docker inspect --format '{{.State.Health.Status}}' "$(docker compose ps -q $s)")"
done
```

```text
proxy: healthy
frontend: healthy
api: healthy
db: healthy
```

The API's healthcheck (`/api -healthcheck`) queries `/api/health`, which pings the database: a running API with a
lost database reports **unhealthy** (step 9 proves it).

## Step 5 · Security, verified

Users, read-only file systems and capabilities of every container:

<!-- test: contains=nonroot; contains=true; output -->
```bash
for s in proxy frontend api db; do
  docker inspect --format "$s: user={{.Config.User}} read-only={{.HostConfig.ReadonlyRootfs}} cap_drop={{.HostConfig.CapDrop}} cap_add={{.HostConfig.CapAdd}}" "$(docker compose ps -q $s)"
done
```

```text
proxy: user=nginx read-only=true cap_drop=[ALL] cap_add=[]
frontend: user=nginx read-only=true cap_drop=[ALL] cap_add=[]
api: user=nonroot:nonroot read-only=true cap_drop=[ALL] cap_add=[]
db: user= read-only=true cap_drop=[ALL] cap_add=[CAP_CHOWN CAP_DAC_OVERRIDE CAP_FOWNER CAP_SETGID CAP_SETUID]
```

PostgreSQL's entrypoint starts as root to prepare the data folder, then switches to the `postgres` user: it keeps only
the five capabilities that needs. Prove the restrictions hold:

<!-- test: contains=Read-only file system; output -->
```bash
docker compose exec proxy sh -c 'echo hacked > /usr/share/nginx/html/index.html' 2>&1 || true
docker compose exec proxy id
```

```text
sh: can't create /usr/share/nginx/html/index.html: Read-only file system
uid=101(nginx) gid=101(nginx) groups=101(nginx)
```

<!-- test: anyof=executable file not found||no such file or directory; output -->
```bash
docker compose exec api sh 2>&1 || true
```

```text
OCI runtime exec failed: exec failed: unable to start container process: exec: "sh": executable file not found in $PATH
```

The API image has no shell at all. The secret is a file inside the container, and not in the environment:

<!-- test: contains=no password in the environment -->
```bash
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$(docker compose ps -q api)" | grep -qi "password=" \
  && echo "password in the environment!" || echo "no password in the environment"
docker compose exec db sh -c 'test -s /run/secrets/db_password && echo "secret mounted at /run/secrets/db_password"'
```

## Step 6 · Networks

<!-- test: contains=capstone_backend; output -->
```bash
docker network ls --filter name=capstone --format '{{.Name}} internal={{.Internal}}'
for s in proxy api db; do
  echo "$s: $(docker inspect --format '{{range $n, $_ := .NetworkSettings.Networks}}{{$n}} {{end}}' "$(docker compose ps -q $s)")"
done
```

```text
capstone_backend internal=true
capstone_edge internal=false
proxy: capstone_edge 
api: capstone_backend capstone_edge 
db: capstone_backend 
```

The proxy cannot even resolve the database's name: it is not on the `backend` network.

<!-- test: anyof=Can't find db||NXDOMAIN||bad address; output -->
```bash
docker compose exec proxy nslookup db 2>&1 | tail -2
```

```text
** server can't find db.: NXDOMAIN

```

## Step 7 · Persistence

Recreate every container (`down` without `-v` keeps the volume), and the orders are still there:

<!-- test: contains=cortado; retry=10 -->
```bash
docker compose down 2>&1 | tail -1
docker compose up -d --wait 2>&1 | tail -1
curl -s http://localhost:8080/api/orders
```

<!-- test: contains=capstone_pgdata -->
```bash
docker volume ls --filter name=capstone
```

## Step 8 · Limits and logs

<!-- test: contains=MiB; output -->
```bash
docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}'
```

```text
NAME                  CPU %     MEM USAGE / LIMIT   PIDS
capstone-proxy-1      0.00%     11.36MiB / 64MiB    15
capstone-api-1        0.00%     2.184MiB / 64MiB    7
capstone-db-1         0.07%     27.34MiB / 256MiB   10
capstone-frontend-1   0.00%     11.2MiB / 32MiB     15
```

Every container has a memory limit (`/ 64MiB`), so one leaking service cannot take the whole host's memory. Logs
rotate, and the API logs structured JSON:

<!-- test: contains=max-size -->
```bash
docker inspect --format '{{.HostConfig.LogConfig.Type}} {{.HostConfig.LogConfig.Config}}' "$(docker compose ps -q api)"
docker compose logs api --no-log-prefix 2>&1 | tail -2
```

## Step 9 · Break it, troubleshoot it, fix it

Stop the database while everything else keeps running:

<!-- test: contains=database unavailable; retry=5 -->
```bash
docker compose stop db 2>&1 | tail -1
curl -s http://localhost:8080/api/health
```

The proxy and the API still run, but the API answers `503 database unavailable`, and within about 30 seconds (three
failed checks, 10 s apart) Docker marks it **unhealthy**:

<!-- test: contains=unhealthy; retry=30; timeout=120 -->
```bash
docker inspect --format '{{.State.Health.Status}}' "$(docker compose ps -q api)"
```

Investigate the way module 17 teaches: state, then logs, then the dependency.

<!-- test: contains=db -->
```bash
docker compose ps -a --format '{{.Service}}: {{.Status}}'
docker inspect --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{end}}' "$(docker compose ps -q api)" | tail -2
```

The `db` service is `Exited`. Fix it, and the API recovers by itself (its connection pool reconnects):

<!-- test: contains="status":"ok"; retry=15 -->
```bash
docker compose start db 2>&1 | tail -1
curl -s http://localhost:8080/api/health
```

## Step 10 · Ship the images to a registry

A local registry stands in for Docker Hub, GHCR or ECR (module 11). The image names in `compose.yaml` already start
with `${REGISTRY}`, so pushing is one command:

<!-- test: contains=pushed -->
```bash
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker compose push --quiet 2>&1 | tail -2
echo "pushed"
```

<!-- test: contains=api; output -->
```bash
curl -s http://localhost:5000/v2/_catalog
```

```text
{"repositories":["capstone/api","capstone/frontend","capstone/proxy"]}
```

Deploy by **digest**, not by tag: a digest names exactly one image forever. Remove the local copy, pull it back by
digest, and compare:

<!-- test: contains=same image -->
```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' localhost:5000/capstone/api:1.0.0)
echo "$digest"
docker image rm -f localhost:5000/capstone/api:1.0.0 > /dev/null
docker pull -q "$digest" > /dev/null
[ "$(docker image inspect --format '{{index .RepoDigests 0}}' "$digest")" = "$digest" ] && echo "same image, pulled by digest"
```

## Step 11 · Continuous integration

[.github/workflows/capstone.yml](../.github/workflows/capstone.yml) runs on every push of this course: it builds the
three images, starts the stack with `docker compose up --wait`, runs the smoke tests of step 3, and on the `main`
branch pushes the images to GitHub Container Registry with the workflow's own `GITHUB_TOKEN` (no stored password).
Module 19 explains each step.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/capstone
docker compose down -v --rmi local 2>&1 | tail -1
docker rm -f registry > /dev/null
docker image rm -f localhost:5000/capstone/api:1.0.0 localhost:5000/capstone/frontend:1.0.0 localhost:5000/capstone/proxy:1.0.0 > /dev/null 2>&1 || true
docker image ls --format '{{.Repository}}' | grep -q capstone && echo "images left" || echo "capstone images removed"
cd ~ && rm -rf ~/docker-practice/capstone
```

Then take the [final exam](final-exam/README.md).
