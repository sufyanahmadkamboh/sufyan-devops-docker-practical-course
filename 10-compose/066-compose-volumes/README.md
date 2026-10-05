# Lesson 066 · Volumes in Compose

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A container's writable layer disappears with the container (lesson 053). Data that must survive (a database, a cache
that must not start empty, uploads) belongs in a **volume**. In Compose you declare named volumes at the top level and
mount them into services; Compose creates them once and keeps them across `down` and `up`, until you explicitly delete
them with `down -v`.

## Visual

```text
 compose.yaml                                    Docker
                                                 ┌───────────────────────────────────────┐
 services:                                       │ container lesson-066-redis-1          │
   redis:                                        │   /data ──────────┐                   │
     volumes:                                    └───────────────────┼───────────────────┘
       - redis-data:/data   ─────────────────────────────────────────┤ mount
 volumes:                                                            ▼
   redis-data:              ──── creates ───▶   volume lesson-066_redis-data (outlives the container)

 docker compose down        containers + network removed, volume KEPT
 docker compose down -v     … and the volume DELETED (the data is gone)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-066 examples/python-api
cp -r 10-compose/066-compose-volumes/examples/. ~/docker-practice/lesson-066/
cd ~/docker-practice/lesson-066
cat compose.yaml
```

## Demonstration

Start the stack and count a few visits:

<!-- test: contains=lesson-066_redis-data; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker volume ls --filter name=lesson-066 --format '{{.Name}}'
```

```text
lesson-066_redis-data
```

<!-- test: retry=15; contains="visits":3; output -->
```bash
curl -s localhost:8080/visits; curl -s localhost:8080/visits; curl -s localhost:8080/visits
```

```text
{"visits":1}
{"visits":2}
{"visits":3}
```

Now remove the whole application (containers and network) and start it again:

<!-- test: contains=lesson-066_redis-data; output -->
```bash
docker compose down 2> /dev/null
docker ps -a --filter label=com.docker.compose.project=lesson-066 --format '{{.Names}}' | wc -l
docker volume ls --filter name=lesson-066 --format '{{.Name}}'
```

```text
0
lesson-066_redis-data
```

<!-- test: retry=15; contains="visits":4; output -->
```bash
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/visits
```

```text
{"visits":4}
```

New containers, same data: the counter continues at 4 because Redis found its files in the volume.

## Command breakdown

| Key / command | What it does |
|---|---|
| `volumes:` (top level) | declare named volumes; Compose names them `PROJECT_NAME` |
| `- redis-data:/data` (service) | mount the named volume at `/data` in the container |
| `- ./src:/app/src` (service) | a bind mount: a folder of your computer (lesson 054) |
| `docker compose down` | remove containers and networks; volumes stay |
| `docker compose down -v` | also remove the project's named volumes |

## Hands-on lab

**Instructions.** Find where the volume is mounted inside the Redis container, and list the files Redis keeps there.

**Expected result.** The mount destination is `/data`; it holds Redis's append-only files (`appendonlydir`).

**Verification.**

<!-- test: contains=/data; contains=appendonlydir -->
```bash
cd ~/docker-practice/lesson-066
docker inspect lesson-066-redis-1 --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
docker compose exec redis ls /data
```

## Break it

A colleague's copy of the file mounts the volume but forgot to declare it at the top level:

<!-- test: fail; contains=undefined volume; output -->
```bash
docker compose -f broken/compose.yaml config 2>&1
```

```text
service "redis" refers to undefined volume redis-data: invalid compose project
```

## Troubleshoot it

`refers to undefined volume redis-data`: in a service, `redis-data:/data` (a name, not a path) means a **named volume**,
and every named volume must be declared under the top-level `volumes:` key. Compose checks this before creating
anything. Compare the two files:

<!-- test: contains=volumes; output -->
```bash
diff broken/compose.yaml compose.yaml || true
```

```text
12a13,15
> 
> volumes:
>   redis-data:                                 # Compose creates it as lesson-066_redis-data
```

## Fix it

Add the declaration (here: copy the correct file) and validate:

<!-- test: contains=redis-data -->
```bash
cp compose.yaml broken/compose.yaml
docker compose -f broken/compose.yaml config --volumes
```

## Practice challenge

Show what `down -v` does to the counter: remove the project with its volumes, start it again, and call `/visits`.

<details>
<summary>Solution</summary>

<!-- test: retry=15; contains="visits":1; output -->
```bash
cd ~/docker-practice/lesson-066
docker compose down -v 2> /dev/null
docker volume ls --filter name=lesson-066 --format '{{.Name}}' | wc -l
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/visits
```

```text
0
{"visits":1}
```

`-v` deleted `lesson-066_redis-data`; the new Redis started empty. Use `down -v` deliberately: on a database it deletes
the data.

</details>

## Real-world example

A team's local development stack keeps PostgreSQL data in a named volume, so `docker compose down` at the end of the
day loses nothing. When someone needs a clean database (a broken migration, a fresh seed), `docker compose down -v` is
the documented reset. In production, data lives on managed storage or a backed-up volume, never only in a container.

## Recap

- Named volumes are declared at the top level and mounted per service (`name:/path`).
- They outlive containers: `down` keeps them, `down -v` deletes them.
- A name in a service's `volumes:` means a named volume, a path (`./dir`) means a bind mount.
- `docker inspect --format '{{range .Mounts}}…'` shows what is mounted where.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-066
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-066
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 067 · Environment variables in Compose](../067-compose-environment/README.md)
