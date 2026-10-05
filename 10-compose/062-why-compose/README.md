# Lesson 062 · Why Docker Compose?

> Level 11 · Docker Compose · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Real applications are several containers: an API, a cache, a database, a proxy. With plain `docker` commands you
create the network, start each container with the right flags, in the right order, and remove everything again by
hand. **Docker Compose** describes the whole application in one file, `compose.yaml`, and manages it with one command:
`docker compose up`. The file lives in Git next to the code, so every developer and every CI job starts exactly the
same stack.

## Visual

```text
 By hand: 5 commands to start, 4 to stop               With Compose: 1 file, 1 command

 docker network create cafe                            compose.yaml
 docker build -t cafe-api .                              services:
 docker run -d --name redis --network cafe redis          api:   build . · port 8080 · REDIS_HOST
 docker run -d --name api --network cafe \               redis: redis:8-alpine
     -p 8080:5000 -e REDIS_HOST=redis cafe-api
 … and the same in reverse to clean up                 docker compose up -d      docker compose down
                                                                │
                                                                ▼
                                         network lesson-062_default ─┬─ lesson-062-api-1    :8080
                                                                     └─ lesson-062-redis-1
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-062 examples/python-api
cp -r 10-compose/062-why-compose/examples/. ~/docker-practice/lesson-062/
cd ~/docker-practice/lesson-062
ls
```

The Flask API of lesson 002 (`app.py`, `requirements.txt`), a `Dockerfile` for it, and a `compose.yaml`. The API
counts visits in Redis: `GET /visits`.

## Demonstration

**The manual way.** Every step is a separate command, and the order matters:

<!-- test: contains=api -->
```bash
docker network create cafe
docker build -q -t cafe-api:dev . > /dev/null
docker run -d --name redis --network cafe redis:8-alpine > /dev/null
docker run -d --name api --network cafe -p 8080:5000 -e REDIS_HOST=redis cafe-api:dev > /dev/null
docker ps --format '{{.Names}}'
```

<!-- test: retry=15; contains=visits; output -->
```bash
curl -s localhost:8080/visits
```

```text
{"visits":1}
```

It works, but you had to remember the network, both names, the port, the variable and the order. Removing it all is
four more commands:

<!-- test -->
```bash
docker rm -f api redis > /dev/null
docker network rm cafe > /dev/null
docker image rm cafe-api:dev > /dev/null
```

**The Compose way.** The same application, written down once:

<!-- test: contains=redis:8-alpine; output -->
```bash
cat compose.yaml
```

```text
services:
  api:
    build: .
    ports:
      - "8080:5000"
    environment:
      REDIS_HOST: redis
  redis:
    image: redis:8-alpine
```

<!-- test: contains=Started; output -->
```bash
docker compose up -d --build 2>&1 | grep -E "Network|Container"
```

```text
 Network lesson-062_default Creating 
 Network lesson-062_default Created 
 Container lesson-062-api-1 Creating 
 Container lesson-062-redis-1 Creating 
 Container lesson-062-redis-1 Created 
 Container lesson-062-api-1 Created 
 Container lesson-062-redis-1 Starting 
 Container lesson-062-api-1 Starting 
 Container lesson-062-redis-1 Started 
 Container lesson-062-api-1 Started 
```

<!-- test: retry=15; contains=visits; output -->
```bash
curl -s localhost:8080/visits
```

```text
{"visits":1}
```

Compose created the network, built the image and started both containers. Names are prefixed with the **project name**
(the folder's name, `lesson-062`), so two projects never collide.

## Command breakdown

| Command | What it does |
|---|---|
| `compose.yaml` | the file Compose reads by default (also `docker-compose.yml`, older name) |
| `docker compose up -d` | create the network, volumes and containers, and start them in the background |
| `--build` | build the images of services with `build:` first (lesson 073) |
| `docker compose ps` | the project's containers |
| `docker compose down` | stop and remove the project's containers and network (lesson 074) |
| project name | the folder name by default; prefixes every container, network and volume |

## Hands-on lab

**Instructions.** List the project's containers with `docker compose ps`, and the network Compose created.

**Expected result.** Two services, `api` and `redis`, both running, and a network `lesson-062_default`.

**Verification.**

<!-- test: contains=lesson-062_default -->
```bash
cd ~/docker-practice/lesson-062
docker compose ps --format '{{.Service}}: {{.State}}'
docker network ls --filter name=lesson-062 --format '{{.Name}}'
```

## Break it

The manual way fails as soon as one step is forgotten. Start a second copy of the API by hand, on the right network,
but forget `-p`:

<!-- test: fail; contains=HTTP 000; output -->
```bash
docker run -d --name forgetful --network lesson-062_default -e REDIS_HOST=redis lesson-062-api > /dev/null
sleep 2
curl -s -w '\nHTTP %{http_code}\n' localhost:8081/visits | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
HTTP 000
```

## Troubleshoot it

`HTTP 000` means curl got no HTTP answer at all: nothing listens on port 8081 of your computer. The container is
running; check which of its ports are published:

<!-- test: contains=forgetful; output -->
```bash
docker ps --filter name=forgetful --format '{{.Names}}  ports: {{.Ports}}'
```

```text
forgetful  ports: 5000/tcp
```

`5000/tcp` without `0.0.0.0:…->` means the port exists inside the container but is not published to the host
(lesson 012). One forgotten flag out of many: that is what Compose prevents.

## Fix it

Do not repeat long `docker run` commands by hand: let Compose apply the file every time.

<!-- test: contains=visits -->
```bash
docker rm -f forgetful > /dev/null
curl -s localhost:8080/visits
```

The Compose service gets the same ports, network and variables on every `up`, for every developer.

## Practice challenge

Stop and remove the whole Compose application with one command, then prove nothing of the project is left (no
containers, no network).

<details>
<summary>Solution</summary>

<!-- test: contains=nothing left; output -->
```bash
cd ~/docker-practice/lesson-062
docker compose down 2>&1 | grep -c Removed
[ -z "$(docker ps -aq --filter label=com.docker.compose.project=lesson-062)" ] && \
  [ -z "$(docker network ls -q --filter name=lesson-062)" ] && echo "nothing left"
```

```text
3
nothing left
```

`down` removed both containers and the network. Compose finds its objects through labels it sets on them
(`com.docker.compose.project`); lesson 101 covers labels.

</details>

## Real-world example

A new developer joins a team with an API, a worker, PostgreSQL and Redis. Instead of a wiki page with fifteen setup
steps, the repository has a `compose.yaml`: `git clone`, `docker compose up`, and the whole stack runs locally in a
minute. CI uses the same file to start the dependencies for integration tests.

## Recap

- Multi-container applications need networks, names, ports, variables and an order: easy to get wrong by hand.
- Compose describes the application in `compose.yaml` and manages it as one project.
- `docker compose up -d` creates everything; `docker compose down` removes it.
- Object names are prefixed with the project name (the folder name by default).

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-062
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-062
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 063 · Your first Compose file](../063-first-compose-file/README.md)
