# Lesson 010 · Container names

> Level 2 · First container · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

Every container has a unique **ID** (64 hexadecimal characters, usually shown shortened to 12) and a unique **name**.
Without `--name`, Docker invents one such as `gallant_ritchie`. Choosing names makes commands readable
(`docker logs api` instead of `docker logs 3f2a9c1e0b77`), and on a user-defined network other containers can reach a
container by its name (lesson 050). Because names are unique, a name can only be used again once the old container is
gone.

## Visual

```text
 docker run nginx:1.30-alpine                 docker run --name web nginx:1.30-alpine
 ┌─────────────────────────────────┐          ┌─────────────────────────────────┐
 │ ID    3f2a9c1e0b77…  (unique)   │          │ ID    8d1e44b2c9a0…  (unique)   │
 │ name  gallant_ritchie (random)  │          │ name  web            (yours)    │
 └─────────────────────────────────┘          └─────────────────────────────────┘

 Every command accepts the full ID, any unique prefix of it, or the name:
   docker stop 8d1e44b2c9a0     docker stop 8d1     docker stop web

 Names are unique per engine, including stopped containers:
   web (exited)  +  docker run --name web …   →   Conflict. The container name "/web" is already in use
```

## Lab setup

No files are needed.

## Demonstration

One container with a random name, one with a chosen name:

<!-- test: contains=web; output -->
```bash
docker run -d nginx:1.30-alpine > /dev/null
docker run -d --name web nginx:1.30-alpine > /dev/null
docker ps --format 'table {{.ID}}\t{{.Names}}\t{{.Image}}'
```

```text
CONTAINER ID   NAMES           IMAGE
4389271662cd   web             nginx:1.30-alpine
f7e1b141e3ae   happy_lamport   nginx:1.30-alpine
```

Any command accepts the name, the ID or a unique prefix of the ID:

<!-- test: contains=same container; output -->
```bash
id=$(docker inspect --format '{{.Id}}' web)
echo "full ID: $id"
[ "$(docker inspect --format '{{.Name}}' "${id:0:4}")" = "/web" ] && echo "the prefix ${id:0:4} and the name web are the same container"
```

```text
full ID: 4389271662cdb393aa8e21820fbe5eb4eb5f267e8190cfeef4f25dcf862b585b
the prefix 4389 and the name web are the same container
```

Rename a container, running or not:

<!-- test: contains=proxy; output -->
```bash
docker rename web proxy
docker ps --filter name=proxy --format '{{.Names}} {{.Status}}'
```

```text
proxy Up 1 second
```

## Command breakdown

| Command / option | Meaning |
|---|---|
| `--name NAME` | give the container a name (letters, digits, `_`, `.`, `-`; must start with a letter or digit) |
| `docker rename OLD NEW` | change a container's name |
| `docker inspect --format '{{.Id}}' NAME` | the full ID of a container |
| `docker ps --filter name=TEXT` | containers whose name **contains** TEXT (`name=^web$` for an exact match) |

## Hands-on lab

**Instructions.** Start a `redis:8-alpine` container in the background named `cache-1`, rename it to `session-cache`,
and print its name and the first 12 characters of its ID.

**Expected result.** `session-cache` followed by a 12-character ID.

**Verification.**

<!-- test: contains=session-cache -->
```bash
docker run -d --name cache-1 redis:8-alpine > /dev/null
docker rename cache-1 session-cache
docker ps --filter name=session-cache --format '{{.Names}} {{.ID}}'
```

## Break it

Start a second container with the name `proxy`, which an existing container already has:

<!-- test: fail; contains=is already in use; output -->
```bash
docker run -d --name proxy nginx:1.30-alpine 2>&1
```

```text
docker: Error response from daemon: Conflict. The container name "/proxy" is already in use by container "4389271662cdb393aa8e21820fbe5eb4eb5f267e8190cfeef4f25dcf862b585b". You have to remove (or rename) that container to be able to reuse that name.

Run 'docker run --help' for more information
```

## Troubleshoot it

`Conflict. The container name "/proxy" is already in use by container "…"`. The error names the container that holds
the name. This happens most often with a container that has **exited**: it no longer shows in `docker ps`, but it still
owns its name. Check all containers with that exact name:

<!-- test: contains=proxy -->
```bash
docker ps -a --filter name=^proxy$ --format '{{.Names}}: {{.Status}} (created {{.RunningFor}})'
```

## Fix it

Decide: is the old container still needed? If not, remove it and reuse the name; if it is, choose another name.

<!-- test: contains=Up -->
```bash
docker rm -f proxy > /dev/null
docker run -d --name proxy nginx:1.30-alpine > /dev/null
docker ps --filter name=^proxy$ --format '{{.Names}}: {{.Status}}'
```

Scripts that start the same container again and again usually do `docker rm -f NAME 2>/dev/null; docker run --name
NAME …`, or use `docker run --rm` so the name is freed when the container exits.

## Practice challenge

Try to name a container `my web`. What does Docker say? Then find the valid name rule in the error and start
a container named `web.v2_blue-1`.

<details>
<summary>Solution</summary>

<!-- test: contains=Invalid container name; contains=web.v2_blue-1; output -->
```bash
docker run -d --name "my web" nginx:1.30-alpine 2>&1 | head -1
docker run -d --name web.v2_blue-1 nginx:1.30-alpine > /dev/null
docker ps --filter name=web.v2 --format '{{.Names}}'
```

```text
docker: Error response from daemon: Invalid container name (my web), only [a-zA-Z0-9][a-zA-Z0-9_.-] are allowed
web.v2_blue-1
```

Names may contain letters, digits, `_`, `.` and `-`, and must start with a letter or digit (`[a-zA-Z0-9][a-zA-Z0-9_.-]`).

</details>

## Real-world example

Teams name containers after their role (`api`, `db`, `proxy`), never after people or random words, so that a teammate
reading `docker ps` on a server understands it at once. Compose names them automatically as `project-service-1`
(lesson 063). Deployment scripts that run `docker run --name api` must handle the old `api` container first, which is
one of the reasons teams move to Compose: it replaces containers by name for you.

## Recap

- Every container has a unique ID and a unique name; commands accept either, or an ID prefix.
- `--name` chooses the name; `docker rename` changes it.
- Names stay taken by exited containers: remove the old container or pick another name.

## Cleanup

<!-- test -->
```bash
docker rm -f $(docker ps -aq --filter ancestor=nginx:1.30-alpine) session-cache > /dev/null
```

Next: [Lesson 011 · Running Nginx](../011-running-nginx/README.md)
