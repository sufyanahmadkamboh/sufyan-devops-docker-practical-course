# Lesson 072 · exec and run

> Level 11 · Docker Compose · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Two ways to run a command for a service, which are easy to confuse:

- `docker compose exec SERVICE CMD` runs the command **in the running container** of that service: same processes,
  same files, same memory. For investigating and administering what is running.
- `docker compose run SERVICE CMD` creates a **new, separate container** from the service's configuration and runs the
  command there. For one-off jobs: migrations, tests, scripts.

## Visual

```text
                      ┌─────────────── lesson-072-api-1 (running) ───────────────┐
 docker compose exec ─┼─▶ new process: sh, python, redis-cli …  next to gunicorn  │
     api CMD          └──────────────────────────────────────────────────────────┘

 docker compose run ──▶ ┌── lesson-072-api-run-1a2b3c (new container) ──┐  same image, environment, networks
     --rm api CMD       │ CMD instead of the default command            │  no published ports (unless --service-ports)
                        └───────────────────── removed afterwards (--rm) ┘
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-072 examples/python-api
cp -r 10-compose/072-compose-exec/examples/. ~/docker-practice/lesson-072/
cd ~/docker-practice/lesson-072
docker compose up -d --build --quiet-build 2> /dev/null
```

## Demonstration

`exec` joins the running container: it sees the API's own processes and environment.

<!-- test: contains=gunicorn; output -->
```bash
docker compose exec api sh -c 'echo "hostname: $(hostname)"; echo "REDIS_HOST=$REDIS_HOST"; ls /proc | grep -c "^[0-9]" ; cat /proc/1/cmdline | tr "\0" " "; echo'
```

```text
hostname: 77ff2fe24d54
REDIS_HOST=redis
5
/usr/local/bin/python3.14 /usr/local/bin/gunicorn --bind 0.0.0.0:5000 --access-logfile - app:app 
```

Process 1 is Gunicorn, the service's main process. `run` instead starts a fresh container with the same configuration:

<!-- test: contains=sh -c; output -->
```bash
docker compose run --rm api sh -c 'echo "hostname: $(hostname)"; cat /proc/1/cmdline | tr "\0" " "; echo' 2> /dev/null
docker compose ps -a --format '{{.Name}}'
```

```text
hostname: 324f91c62285
sh -c echo "hostname: $(hostname)"; cat /proc/1/cmdline | tr "\0" " "; echo 
lesson-072-api-1
lesson-072-redis-1
```

Another hostname, and process 1 is our command. `--rm` removed the container afterwards; only the two service
containers remain. The new container was on the project network, so it could reach `redis` too:

<!-- test: contains=visits; output -->
```bash
docker compose run --rm api python -c "import app; print(app.app.test_client().get('/visits').json)" 2> /dev/null
```

```text
{'visits': 1}
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker compose exec SERVICE CMD` | run CMD in the service's running container |
| `exec -T` | no pseudo-terminal: for scripts and pipes (`… exec -T db psql < dump.sql`) |
| `exec -u USER`, `exec -w DIR`, `exec -e VAR=x` | as another user, in another directory, with an extra variable |
| `docker compose run --rm SERVICE CMD` | a new one-off container of the service, removed afterwards |
| `run --no-deps` | do not start the service's dependencies |
| `run --service-ports` | publish the service's ports (off by default for `run`) |

## Hands-on lab

**Instructions.** Use `exec` and Redis's own client to read the `visits` key directly from Redis.

**Expected result.** The number of visits so far (at least `1`).

**Verification.**

<!-- test: contains=1 -->
```bash
cd ~/docker-practice/lesson-072
docker compose exec redis redis-cli GET visits
```

## Break it

Stop the API, then try to look inside it:

<!-- test: fail; contains=is not running; output -->
```bash
docker compose stop api 2> /dev/null
docker compose exec api ls 2>&1
```

```text
service "api" is not running
```

## Troubleshoot it

`exec` needs a running container: it starts a process inside an existing one. Check the state:

<!-- test: contains=exited; output -->
```bash
docker compose ps -a --format '{{.Service}}: {{.State}} ({{.Status}})'
```

```text
api: exited (Exited (0) Less than a second ago)
redis: running (Up 6 seconds)
```

When the container crashed instead of being stopped, `exec` is impossible too, and `docker compose logs api` is the
first place to look (lesson 071).

## Fix it

Start it again, or use `run` when you need the image and configuration but not the running container (for example to
inspect files of a service that crashes at start):

<!-- test: contains=app.py -->
```bash
docker compose run --rm --no-deps api ls 2> /dev/null
docker compose start api 2> /dev/null
docker compose exec api ls
```

## Practice challenge

Pipe a command from your computer into a container: count the lines of `app.py` inside the API container with
`wc -l`, feeding it through standard input (`exec -T`).

<details>
<summary>Solution</summary>

<!-- test: contains=app.py; output -->
```bash
cd ~/docker-practice/lesson-072
docker compose exec -T api sh -c 'wc -l' < app.py | sed 's/$/ lines in app.py/'
```

```text
28 lines in app.py
```

Without `-T`, Compose allocates a terminal when you run it interactively, and input redirection does not mix well with
terminals. `-T` is how scripts and CI jobs run commands in containers (database dumps and restores work the same way).

</details>

## Real-world example

A team runs database migrations as a one-off job before each deployment: `docker compose run --rm api flask db upgrade`.
It uses the new image and the production configuration but does not touch the running API containers. When an incident
happens, the engineer on call uses `docker compose exec api sh` to look at the running container's environment and
files, without restarting it.

## Recap

- `exec`: a new process in the running container (needs it running).
- `run`: a new container from the service's configuration (use `--rm`).
- `exec -T` for scripts and pipes; `run --no-deps`, `--service-ports` as needed.
- A stopped or crashed service: read its logs, then `start` it or investigate with `run`.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-072
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-072
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 073 · Building images with Compose](../073-compose-build/README.md)
