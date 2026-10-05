# Lesson 064 · Services

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A **service** is one component of the application: Compose runs one or more containers for it, all from the same
configuration. This lesson covers the keys every service uses: where the image comes from (`image:` or `build:`), the
command, the ports, the restart policy, and how many copies run (`--scale`).

## Visual

```text
 service "api"                                         service "redis"
 ┌───────────────────────────────────────┐             ┌──────────────────────────────────────┐
 │ build: .        → image lesson-064-api│             │ image: redis:8-alpine                │
 │ ports: 8080:5000                      │             │ command: redis-server --appendonly …  │
 │ restart: unless-stopped               │             │ restart: unless-stopped              │
 └──────────────┬────────────────────────┘             └──────────────────┬───────────────────┘
                │ --scale api=2                                            │ 1 replica
                ▼                                                          ▼
   lesson-064-api-1   lesson-064-api-2                          lesson-064-redis-1
   (each replica needs its own host port)
```

| Key | Meaning |
|---|---|
| `image:` | run an existing image (pulled if missing) |
| `build:` | build the image from a Dockerfile (lesson 073) |
| `command:` | replace the image's default command (`CMD`) |
| `ports:` | publish `HOST:CONTAINER` ports |
| `restart:` | `no` (default), `on-failure`, `unless-stopped`, `always` |

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-064 examples/python-api
cp -r 10-compose/064-compose-services/examples/. ~/docker-practice/lesson-064/
cd ~/docker-practice/lesson-064
cat compose.yaml
```

## Demonstration

Start the project and list its services and containers:

<!-- test: contains=redis; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose config --services
docker compose ps --no-trunc --format '{{.Name}}  image={{.Image}}  command={{.Command}}'
```

```text
api
redis
lesson-064-api-1  image=lesson-064-api  command="gunicorn --bind 0.0.0.0:5000 --access-logfile - app:app"
lesson-064-redis-1  image=redis:8-alpine  command="docker-entrypoint.sh redis-server --appendonly yes"
```

The `api` image was built and named `PROJECT-SERVICE`; `redis` used the image as it is, with the command from the file.

**Restart policy.** Stop the API's main process from inside, the way a crash would:

<!-- test: retry=15; contains=visits -->
```bash
curl -s localhost:8080/visits
```

<!-- test -->
```bash
docker compose exec api sh -c 'kill 1'
```

<!-- test: contains=restarts: 1; output; retry=10 -->
```bash
docker inspect lesson-064-api-1 --format 'policy: {{.HostConfig.RestartPolicy.Name}}, restarts: {{.RestartCount}}, state: {{.State.Status}}'
```

```text
policy: unless-stopped, restarts: 1, state: running
```

Docker started the container again by itself. Without a policy (`restart: no`), it would stay `exited`.

## Command breakdown

| Command | What it does |
|---|---|
| `docker compose config --services` | the services in the file |
| `docker compose ps --format '{{.Name}} …'` | one line per container, with the fields you choose |
| `docker compose exec api sh -c 'kill 1'` | stop process 1 of the container (its main process); `kill` is a shell command |
| `{{.RestartCount}}` | how many times Docker restarted the container |
| `docker compose up -d --scale api=2` | run two containers for `api` |

## Hands-on lab

**Instructions.** Stop the `redis` service with `docker compose stop redis`, wait a few seconds, and check whether its
restart policy brought it back.

**Expected result.** It stays `exited`: `unless-stopped` never restarts a container you stopped yourself. Start it
again with `docker compose start redis`.

**Verification.**

<!-- test: contains=exited; contains=running -->
```bash
cd ~/docker-practice/lesson-064
docker compose stop redis 2> /dev/null; sleep 3
docker inspect lesson-064-redis-1 --format '{{.State.Status}}'
docker compose start redis 2> /dev/null
docker inspect lesson-064-redis-1 --format '{{.State.Status}}'
```

## Break it

More traffic: run two copies of the API.

<!-- test: fail; contains=port is already allocated; output -->
```bash
docker compose up -d --scale api=2 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint lesson-064-api-2 (b5ff8a2ebfe2758b37ebdb39d2d16dfbadb6119e46f1fb9e5a11bc8775083d96): Bind for 0.0.0.0:8080 failed: port is already allocated
```

## Troubleshoot it

`Bind for 0.0.0.0:8080 failed: port is already allocated`: the second replica asked for host port 8080, which the first
one already holds. A host port can belong to one container only. The failed replica was created but never started:

<!-- test: contains=api-2; output -->
```bash
docker compose ps -a --format '{{.Name}}: {{.State}}'
```

```text
lesson-064-api-1: running
lesson-064-api-2: created
lesson-064-redis-1: running
```

## Fix it

Give the service a **range** of host ports: each replica takes a free one.

<!-- test: contains=api-2 -->
```bash
sed -i.bak 's/"8080:5000"/"8080-8081:5000"/' compose.yaml && rm compose.yaml.bak
docker compose up -d --scale api=2 2> /dev/null
docker compose ps --format '{{.Name}}  {{.Ports}}'
```

In production the replicas sit behind a reverse proxy or load balancer, and only the proxy publishes a port (the
capstone does this with Nginx).

## Practice challenge

Both replicas share the same Redis. Call `/visits` on port 8080 and on port 8081, and show that the counter is shared
while `/` reports two different container hostnames.

<details>
<summary>Solution</summary>

<!-- test: retry=15; contains=visits; output -->
```bash
cd ~/docker-practice/lesson-064
curl -s localhost:8080/visits
curl -s localhost:8081/visits
curl -s localhost:8080/ | grep -o '"hostname":"[0-9a-f]*"'
curl -s localhost:8081/ | grep -o '"hostname":"[0-9a-f]*"'
```

```text
{"visits":2}
{"visits":3}
"hostname":"7b94b3ccb608"
"hostname":"ac259f414814"
```

The state lives in Redis, not in the API containers: that is what makes the API safe to scale (stateless services).

</details>

## Real-world example

A team runs its API with `restart: unless-stopped` on a single server, so a crash or a reboot of Docker brings it back
without anyone logging in. When load grows, they scale the stateless API service, keep one database, and put a proxy in
front. When they outgrow one server, Kubernetes takes over the same ideas: replicas, restart policies, one entry point.

## Recap

- A service = configuration for one or more identical containers.
- `image:` uses an image, `build:` builds one; `command:` replaces the default command.
- `restart: unless-stopped` restarts crashed containers, not ones you stopped.
- Replicas cannot share a fixed host port: use a range, or a proxy in front.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-064
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-064
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 065 · Networking in Compose](../065-compose-networking/README.md)
