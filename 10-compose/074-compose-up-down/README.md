# Lesson 074 · up, down and the project lifecycle

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

`up` is not only "start": it **converges** the running project to the file. It creates what is missing, recreates
containers whose configuration changed, and leaves the rest alone. `stop`/`start` pause and resume containers without
removing them; `down` removes them. What `down` removes can be widened: volumes (`-v`), images (`--rmi`), and
containers of services that are no longer in the file (`--remove-orphans`).

## Visual

```text
                 up -d (create + start, or recreate on change)
   (nothing) ─────────────────────────────────────────────▶ running ◀──┐
       ▲                                                       │       │ start / restart
       │ down                                             stop │       │
       │  + -v            named volumes                        ▼       │
       │  + --rmi local   images built by the project       stopped ───┘
       │  + --remove-orphans  containers of removed services
       └───────────────────────────────────────────────────────┘

 docker compose up -d     after editing compose.yaml: only changed services are recreated
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-074 examples/python-api
cp -r 10-compose/074-compose-up-down/examples/. ~/docker-practice/lesson-074/
cd ~/docker-practice/lesson-074
cat compose.yaml
```

## Demonstration

The first `up` creates everything:

<!-- test: contains=Created; output -->
```bash
docker compose up -d --build --quiet-build 2>&1 | grep -E "Container .* (Created|Started|Running|Recreated) *$"
```

```text
 Container lesson-074-api-1 Created 
 Container lesson-074-redis-1 Created 
 Container lesson-074-worker-1 Created 
 Container lesson-074-worker-1 Started 
 Container lesson-074-redis-1 Started 
 Container lesson-074-api-1 Started 
```

A second `up` with an unchanged file changes nothing:

<!-- test: contains=Running; absent=Recreated; output -->
```bash
docker compose up -d 2>&1 | grep -E "Container .* (Created|Started|Running|Recreated) *$"
```

```text
 Container lesson-074-api-1 Running 
 Container lesson-074-worker-1 Running 
 Container lesson-074-redis-1 Running 
```

Change one service's configuration, and only that service is recreated:

<!-- test: contains=api-1 Recreated; output -->
```bash
sed -i.bak 's/      REDIS_HOST: redis/      REDIS_HOST: redis\
      GREETING: Hello after up/' compose.yaml && rm compose.yaml.bak
docker compose up -d 2>&1 | grep -E "Container .* (Created|Started|Running|Recreated) *$"
```

```text
 Container lesson-074-redis-1 Running 
 Container lesson-074-worker-1 Running 
 Container lesson-074-api-1 Recreated 
 Container lesson-074-api-1 Started 
```

`stop` keeps the containers (and their writable layers); `start` resumes them:

<!-- test: contains=exited; contains=running; output -->
```bash
docker compose stop 2> /dev/null
docker compose ps -a --format '{{.Service}}: {{.State}}'
docker compose start 2> /dev/null
docker compose ps -a --format '{{.Service}}: {{.State}}'
```

```text
api: exited
redis: exited
worker: exited
api: running
redis: running
worker: running
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker compose up -d` | create missing, recreate changed, start stopped; leave the rest |
| `up -d --force-recreate` | recreate every container, changed or not |
| `up -d SERVICE` | only this service (and its dependencies) |
| `docker compose stop` / `start` / `restart` | stop, start, restart without removing |
| `docker compose down` | remove containers and networks |
| `down -v` / `down --rmi local` | also the named volumes / the images the project built |
| `down --remove-orphans`, `up --remove-orphans` | also containers of services no longer in the file |

## Hands-on lab

**Instructions.** Make `down` remove everything the project created except the pulled `redis` and `alpine` images:
containers, network, the volume and the built `api` image. Then verify that nothing of the project is left.

**Expected result.** No container, network or volume named `lesson-074…`, and no image `lesson-074-api`.

**Verification.**

<!-- test: contains=0 0 0 0 -->
```bash
cd ~/docker-practice/lesson-074
docker compose down -v --rmi local 2> /dev/null
echo "$(docker ps -aq --filter name=lesson-074 | wc -l) $(docker network ls -q --filter name=lesson-074 | wc -l) $(docker volume ls -q --filter name=lesson-074 | wc -l) $(docker image ls -q lesson-074-api | wc -l)" | tr -s ' '
```

Start it again for the next steps:

<!-- test -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
```

## Break it

The team no longer needs the `worker` service and deletes it from the file. Everyone runs `up` as usual:

<!-- test: contains=orphan; output -->
```bash
awk '/^  worker:/ { skip = 1; next } /^[^ ]/ { skip = 0 } skip && /^    / { next } { print }' compose.yaml > compose.new
mv compose.new compose.yaml
docker compose config --services
docker compose up -d 2>&1 | grep -i orphan
```

```text
api
redis
time="2026-10-05T19:15:52+02:00" level=warning msg="Found orphan containers ([lesson-074-worker-1]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up."
```

## Troubleshoot it

A warning, not an error, so it is easy to miss. The old container still runs, uses resources, and (for a real worker)
may still be processing jobs with old code:

<!-- test: contains=worker; output -->
```bash
docker ps --filter label=com.docker.compose.project=lesson-074 --format '{{.Names}}: {{.Status}}'
```

```text
lesson-074-worker-1: Up 1 second
lesson-074-redis-1: Up 1 second
lesson-074-api-1: Up 1 second
```

Compose finds a project's containers through the `com.docker.compose.project` label; a container whose service is no
longer in the file is an **orphan**, and Compose does not remove it unless told to.

## Fix it

<!-- test: absent=worker; output -->
```bash
docker compose up -d --remove-orphans 2> /dev/null
docker ps --filter label=com.docker.compose.project=lesson-074 --format '{{.Names}}'
```

```text
lesson-074-redis-1
lesson-074-api-1
```

## Practice challenge

Recreate only the `api` container (without changing the file) and show that `redis` kept running: its start time must
not change.

<details>
<summary>Solution</summary>

<!-- test: contains=redis unchanged; output -->
```bash
cd ~/docker-practice/lesson-074
before=$(docker inspect lesson-074-redis-1 --format '{{.State.StartedAt}}')
docker compose up -d --force-recreate --no-deps api 2> /dev/null
after=$(docker inspect lesson-074-redis-1 --format '{{.State.StartedAt}}')
[ "$before" = "$after" ] && echo "redis unchanged, api recreated at $(docker inspect lesson-074-api-1 --format '{{.State.StartedAt}}')"
```

```text
redis unchanged, api recreated at 2026-10-05T17:15:56.715289908Z
```

`--force-recreate` recreates even an unchanged container; `--no-deps` keeps Compose away from the dependencies.

</details>

## Real-world example

On a single-server deployment, the release script is `docker compose pull && docker compose up -d --remove-orphans`:
only services with a new image or new configuration are recreated, the database container keeps running, and services
removed from the file disappear. `down -v` never appears in that script: it would delete the production data.

## Recap

- `up -d` converges to the file: creates, recreates on change, starts; unchanged containers stay.
- `stop`/`start` keep containers; `down` removes them (`-v` volumes, `--rmi local` built images).
- Removed services leave orphans: `--remove-orphans`.
- `--force-recreate` and `--no-deps` give finer control.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-074
docker compose down -v --rmi local --remove-orphans 2> /dev/null
rm -rf ~/docker-practice/lesson-074
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 075 · What is a registry?](../../11-registry/075-what-is-a-registry/README.md)
