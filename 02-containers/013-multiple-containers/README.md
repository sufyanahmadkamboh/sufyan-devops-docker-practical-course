# Lesson 013 · Running multiple containers

> Level 3 · Working with containers · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Real systems are several containers: a website, an API, a cache, a database. Each container is independent: its own
process, its own file system, its own published ports. This lesson runs several at once and shows how to manage them as
a **group**, with labels and filters, instead of one name at a time. Compose (module 10) automates this; here you learn
what it does under the hood.

## Visual

```text
  localhost:8080 ──▶ ┌──────────────┐   localhost:8081 ──▶ ┌──────────────┐   (no published port)
                     │ site-a       │                      │ site-b       │   ┌──────────────┐
                     │ nginx :80    │                      │ nginx :80    │   │ cache        │
                     │ "Site a"     │                      │ "Site b"     │   │ redis :6379  │
                     └──────────────┘                      └──────────────┘   └──────────────┘
                     label project=lesson-013  ─────────── on all three ──────────────────────
  Act on the group:  docker ps --filter label=project=lesson-013
                     docker stop $(docker ps -q --filter label=project=lesson-013)
```

## Lab setup

No files are needed.

## Demonstration

Start two websites with different content and a Redis cache, all marked with the same **label** (a `key=value` tag you
choose; lesson 101):

<!-- test: contains=done -->
```bash
for site in a b; do
  port=$([ "$site" = a ] && echo 8080 || echo 8081)
  docker run -d --name "site-$site" --label project=lesson-013 -p "$port:80" nginx:1.30-alpine \
    sh -c "echo '<h1>Site $site</h1>' > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'" > /dev/null
done
docker run -d --name cache --label project=lesson-013 redis:8-alpine > /dev/null
echo done
```

`sh -c "… && exec nginx -g 'daemon off;'"` writes a page, then replaces the shell with Nginx in the foreground (the
image's normal command). Each site answers with its own content:

<!-- test: contains=Site a; contains=Site b; retry=10; output -->
```bash
curl -s http://localhost:8080
curl -s http://localhost:8081
```

```text
<h1>Site a</h1>
<h1>Site b</h1>
```

List the group by its label:

<!-- test: contains=cache; output -->
```bash
docker ps --filter label=project=lesson-013 --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
```

```text
NAMES     IMAGE               PORTS
cache     redis:8-alpine      6379/tcp
site-b    nginx:1.30-alpine   0.0.0.0:8081->80/tcp, [::]:8081->80/tcp
site-a    nginx:1.30-alpine   0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

Stop and start the whole group at once:

<!-- test: contains=running: 0; contains=running: 3; output -->
```bash
docker stop $(docker ps -q --filter label=project=lesson-013) > /dev/null
echo "running: $(docker ps -q --filter label=project=lesson-013 | wc -l | tr -d ' ')"
docker start $(docker ps -aq --filter label=project=lesson-013) > /dev/null
echo "running: $(docker ps -q --filter label=project=lesson-013 | wc -l | tr -d ' ')"
```

```text
running: 0
running: 3
```

## Command breakdown

| Command / part | Meaning |
|---|---|
| `--label KEY=VALUE` | attach metadata to a container; filter on it later |
| `--filter label=KEY=VALUE` | only containers with that label |
| `$(docker ps -q --filter …)` | the IDs of the matching containers, as arguments for another command |
| `docker stop A B C` / `docker start A B C` | commands accept several containers |
| `exec nginx -g 'daemon off;'` | replace the shell with Nginx running in the foreground |

## Hands-on lab

**Instructions.** Add a third website `site-c` on port 8082 with the content `Site c`, with the same label, and show
that the group now has four containers.

**Expected result.** `Site c` from port 8082, and `4` containers with the label.

**Verification.**

<!-- test -->
```bash
docker run -d --name site-c --label project=lesson-013 -p 8082:80 nginx:1.30-alpine \
  sh -c "echo '<h1>Site c</h1>' > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"
```

<!-- test: contains=Site c; contains=4; retry=10 -->
```bash
curl -s http://localhost:8082
docker ps -q --filter label=project=lesson-013 | wc -l | tr -d ' '
```

## Break it

A cleanup script stops every container of a project. Run it for a project that has no containers:

<!-- test: fail; contains=requires at least 1 argument; output -->
```bash
docker stop $(docker ps -q --filter label=project=lesson-999) 2>&1
```

```text
docker: 'docker stop' requires at least 1 argument

Usage:  docker stop [OPTIONS] CONTAINER [CONTAINER...]

See 'docker stop --help' for more information
```

## Troubleshoot it

`'docker stop' requires at least 1 argument`: the filter matched nothing, so `$(…)` expanded to nothing and the command
became plain `docker stop`. Run the inner command alone to see what it returns:

<!-- test: contains=matches: 0 -->
```bash
echo "matches: $(docker ps -q --filter label=project=lesson-999 | wc -l | tr -d ' ')"
```

## Fix it

Only call `docker stop` when there is something to stop:

<!-- test: contains=nothing to stop -->
```bash
ids=$(docker ps -q --filter label=project=lesson-999)
if [ -n "$ids" ]; then docker stop $ids; else echo "nothing to stop"; fi
```

(`docker ps -q … | xargs -r docker stop` does the same with GNU `xargs`.)

## Practice challenge

Start five Nginx containers in a loop, `web-1` … `web-5`, on ports 8091–8095 with the label `project=load-test`, then
prove that every one of them answers, and remove the whole group with one command.

<details>
<summary>Solution</summary>

<!-- test -->
```bash
for i in 1 2 3 4 5; do
  docker run -d --name "web-$i" --label project=load-test -p "809$i:80" nginx:1.30-alpine > /dev/null
done
```

<!-- test: contains=5 of 5 answered; retry=10; output -->
```bash
ok=0
for i in 1 2 3 4 5; do curl -sf "http://localhost:809$i" > /dev/null && ok=$((ok + 1)); done
echo "$ok of 5 answered"
```

```text
5 of 5 answered
```

<!-- test: contains=removed: 5 -->
```bash
echo "removed: $(docker rm -f $(docker ps -aq --filter label=project=load-test) | wc -l | tr -d ' ')"
```

</details>

## Real-world example

A developer runs the shop's frontend, API, Redis and Postgres locally to reproduce a bug. With one container per
service, each one can be restarted, upgraded or replaced without touching the others. Labels such as `project=shop` (and
the ones Compose adds automatically, `com.docker.compose.project`) let scripts and tools find all containers of a
system, for example to clean up after a test run in CI.

## Recap

- Each container is independent: its own process, files and published ports.
- Labels group containers; `--filter label=…` with `-q` acts on the whole group.
- `$(docker ps -q …)` can be empty: guard commands that need at least one ID.
- Running many containers by hand is repetitive; Compose (module 10) describes them in one file.

## Cleanup

<!-- test -->
```bash
docker rm -f $(docker ps -aq --filter label=project=lesson-013) > /dev/null
```

Next: [Lesson 014 · Container logs](../014-container-logs/README.md)
