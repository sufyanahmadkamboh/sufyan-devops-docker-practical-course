# Lesson 070 · Profiles

> Level 11 · Docker Compose · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Some services are not needed every time: a debugging shell, an admin UI, a job that loads test data, a load generator.
**Profiles** keep them in the same `compose.yaml` but start them only on request. A service without `profiles:` always
starts; a service with `profiles: [debug]` starts only when the `debug` profile is active.

## Visual

```text
 compose.yaml              docker compose up        --profile seed         --profile debug
 api                       ✓                        ✓                      ✓
 redis                     ✓                        ✓                      ✓
 seed   profiles: [seed]   ·                        ✓ (runs once)          ·
 tools  profiles: [debug]  ·                        ·                      ✓

 activate:  --profile NAME   (several: --profile a --profile b)
            COMPOSE_PROFILES=a,b   (environment variable or .env)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-070 examples/python-api
cp -r 10-compose/070-compose-profiles/examples/. ~/docker-practice/lesson-070/
cd ~/docker-practice/lesson-070
cat compose.yaml
```

## Demonstration

Without a profile, only the two core services start:

<!-- test: contains=redis; absent=tools; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose ps --format '{{.Service}}'
```

```text
api
redis
```

All services of the file, and the profiles that exist:

<!-- test: contains=debug; output -->
```bash
docker compose --profile "*" config --services
docker compose config --profiles
```

```text
api
redis
seed
tools
debug
seed
```

Load test data with the `seed` profile, then use the debugging shell of the `debug` profile:

<!-- test: retry=15; contains="visits":101; output -->
```bash
docker compose --profile seed up -d 2> /dev/null
sleep 2
curl -s localhost:8080/visits
```

```text
{"visits":101}
```

<!-- test: contains=tools; output -->
```bash
COMPOSE_PROFILES=debug docker compose up -d 2> /dev/null
docker compose ps --format '{{.Service}}'
```

```text
api
redis
tools
```

## Command breakdown

| Command / key | What it does |
|---|---|
| `profiles: [name]` | the service belongs to that profile and is skipped by default |
| `docker compose --profile NAME up` | also start the services of that profile |
| `COMPOSE_PROFILES=a,b` | the same, as an environment variable (or in `.env`) |
| `docker compose --profile "*" …` | all profiles |
| `docker compose config --profiles` | the profiles defined in the file |
| `docker compose run --rm SERVICE` | run one service, even one with a profile (lesson 072) |

## Hands-on lab

**Instructions.** Use the `tools` container to look up the address of `redis` on the project network.

**Expected result.** An IP address followed by the name `redis`.

**Verification.**

<!-- test: contains=redis -->
```bash
cd ~/docker-practice/lesson-070
docker compose exec tools getent hosts redis
```

## Break it

Someone decides "the API needs test data" and makes it depend on `seed`:

<!-- test: fail; contains=undefined service; output -->
```bash
cp compose.yaml compose.good.yaml
cp broken/compose.yaml compose.yaml
docker compose up -d 2>&1
```

```text
service "api" depends on undefined service "seed": invalid compose project
```

## Troubleshoot it

`depends on undefined service "seed"`: `seed` is in the file, but its profile is not active, so for this command it
does not exist, and a service that always starts cannot depend on it. With the profile active, the file is valid:

<!-- test: contains=seed; output -->
```bash
docker compose --profile seed config --services
```

```text
seed
api
redis
```

## Fix it

An always-on service should not depend on an optional one. Either remove the dependency, or mark it optional with
`required: false` (Compose then waits for `seed` only when it is part of the run):

<!-- test: contains=api; output -->
```bash
cp compose.good.yaml compose.yaml
docker compose config --services
```

```text
api
redis
```

The original file has no dependency: `seed` is a job you run when you need it, `--profile seed`.

## Practice challenge

Run the `seed` job once more, as a one-off container that is removed afterwards, without starting the `debug`
profile, and check that the counter is reset to 100.

<details>
<summary>Solution</summary>

<!-- test: retry=15; contains="visits":101; output -->
```bash
cd ~/docker-practice/lesson-070
docker compose run --rm seed 2> /dev/null
curl -s localhost:8080/visits
```

```text
OK
{"visits":101}
```

`docker compose run SERVICE` starts one service even when its profile is not active; `--rm` removes it after it exits.
`OK` is Redis's answer to `SET`.

</details>

## Real-world example

A team's `compose.yaml` holds the application, a `monitoring` profile (Prometheus and Grafana), a `seed` profile for
demo data and a `debug` profile with database admin tools. New developers run `docker compose up`; whoever investigates
a performance problem adds `--profile monitoring`. One file, no copies drifting apart.

## Recap

- `profiles: [name]` makes a service optional; services without profiles always start.
- Activate with `--profile name` or `COMPOSE_PROFILES`.
- An always-on service cannot depend on an inactive one (or use `required: false`).
- `docker compose run --rm SERVICE` runs a one-off job, profile or not.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-070
docker compose --profile "*" down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-070
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 071 · Logs](../071-compose-logs/README.md)
