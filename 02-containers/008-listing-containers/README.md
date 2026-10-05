# Lesson 008 · Listing containers

> Level 2 · First container · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

`docker ps` is the command you will type most often. By default it lists **running** containers only; `-a` adds the
stopped ones. Filters (`--filter`) narrow the list down, `--format` chooses the columns, and `-q` prints only IDs for use
in other commands. On a busy machine, these options are the difference between finding your container in a second and
scrolling through a wall of text.

## Visual

```text
 docker ps                         docker ps -a                           docker ps -q
 ┌──────────────────────┐          ┌──────────────────────────────┐       ┌──────────────┐
 │ running containers   │          │ running                      │       │ 3f2a9c1e0b77 │
 │  web    Up 2 minutes │          │ + created (never started)    │       │ 8d1e44b2c9a0 │
 └──────────────────────┘          │ + exited  (stopped)          │       └──────────────┘
                                   │ + paused, restarting, dead   │        only IDs: input
                                   └──────────────────────────────┘        for other commands

 Columns:  CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES
 Narrow:   --filter status=exited   --filter name=web   --filter ancestor=nginx:1.30-alpine
 Shape:    --format 'table {{.Names}}\t{{.Status}}'      -n 3 (last 3)      -l (latest)
```

## Lab setup

Create a few containers in different states: one running, one that exits successfully, one that fails, one never
started:

<!-- test: contains=done -->
```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
docker run --name job-ok alpine:3.23 true
docker run --name job-failed alpine:3.23 sh -c 'exit 3' || true
docker create --name not-started alpine:3.23 echo hi > /dev/null
echo done
```

## Demonstration

Running containers only:

<!-- test: contains=web; absent=job-ok; output -->
```bash
docker ps
```

```text
CONTAINER ID   IMAGE               COMMAND                  CREATED         STATUS        PORTS     NAMES
1cb0571d46d6   nginx:1.30-alpine   "/docker-entrypoint.…"   2 seconds ago   Up 1 second   80/tcp    web
```

All containers, with their status:

<!-- test: contains=Exited (3); contains=Created; output -->
```bash
docker ps -a
```

```text
CONTAINER ID   IMAGE               COMMAND                  CREATED         STATUS                              PORTS     NAMES
6451be625cfb   alpine:3.23         "echo hi"                1 second ago    Created                                       not-started
1123bafe7de1   alpine:3.23         "sh -c 'exit 3'"         1 second ago    Exited (3) Less than a second ago             job-failed
c0c0b2c921d9   alpine:3.23         "true"                   2 seconds ago   Exited (0) 1 second ago                       job-ok
1cb0571d46d6   nginx:1.30-alpine   "/docker-entrypoint.…"   3 seconds ago   Up 2 seconds                        80/tcp    web
```

`Exited (0)` succeeded, `Exited (3)` failed with exit code 3, `Created` never started. The full table is wide; choose
the columns you need:

<!-- test: contains=job-failed; output -->
```bash
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```text
NAMES         IMAGE               STATUS
not-started   alpine:3.23         Created
job-failed    alpine:3.23         Exited (3) 1 second ago
job-ok        alpine:3.23         Exited (0) 1 second ago
web           nginx:1.30-alpine   Up 2 seconds
```

Filters combine with every other option. Only the stopped containers:

<!-- test: contains=job-ok; absent=web; output -->
```bash
docker ps -a --filter status=exited --format '{{.Names}}'
```

```text
job-failed
job-ok
```

Only IDs, ready to pass to another command (here counted: the two exited containers):

<!-- test: contains=2 -->
```bash
docker ps -aq --filter status=exited | wc -l | tr -d ' '
```

## Command breakdown

| Option | Meaning |
|---|---|
| `-a`, `--all` | include stopped containers |
| `-q`, `--quiet` | print only container IDs |
| `-l`, `--latest` / `-n N` | the most recently created container / the last N |
| `--filter status=…` | `created`, `running`, `paused`, `restarting`, `removing`, `exited`, `dead` |
| `--filter name=TEXT` | names containing TEXT |
| `--filter ancestor=IMAGE` | created from IMAGE |
| `--filter exited=CODE` | stopped with that exit code |
| `--format 'table {{.Names}}\t{{.Status}}'` | choose columns (`table` keeps the header) |
| `--no-trunc` | do not shorten IDs and commands |
| `-s`, `--size` | the size of each container's writable layer |

## Hands-on lab

**Instructions.** List the names and commands of all containers created from `alpine:3.23`, with the full commands not
shortened.

**Expected result.** `job-ok`, `job-failed` and `not-started`, with commands such as `"sh -c 'exit 3'"`.

**Verification.**

<!-- test: contains=job-failed; contains=not-started; absent=web -->
```bash
docker ps -a --filter ancestor=alpine:3.23 --no-trunc --format 'table {{.Names}}\t{{.Command}}'
```

## Break it

You remember that stopped containers are "stopped", so you filter on that:

<!-- test: fail; contains=invalid filter; output -->
```bash
docker ps -a --filter status=stopped
```

```text
Error response from daemon: invalid filter 'status=stopped': invalid value for state (stopped): must be one of created, running, paused, restarting, removing, exited, dead
```

## Troubleshoot it

`invalid value for state (stopped): must be one of created, running, paused, restarting, removing, exited, dead`. The
error lists every valid value: Docker calls a stopped container **exited**. Filter keys and values are fixed words,
listed in `docker ps --help` and in the error itself. Read the whole error line before searching the web.

## Fix it

<!-- test: contains=job-failed -->
```bash
docker ps -a --filter status=exited --format '{{.Names}}: {{.Status}}'
```

## Practice challenge

Show only the containers that **failed**, i.e. exited with code 3, with their name and status. Then show the size of the
writable layer of every container.

<details>
<summary>Solution</summary>

<!-- test: contains=job-failed; output -->
```bash
docker ps -a --filter exited=3 --format '{{.Names}}: {{.Status}}'
docker ps -a -s --format 'table {{.Names}}\t{{.Size}}'
```

```text
job-failed: Exited (3) 2 seconds ago
NAMES         SIZE
not-started   4.1kB (virtual 9.1MB)
job-failed    4.1kB (virtual 9.1MB)
job-ok        4.1kB (virtual 9.1MB)
web           81.9kB (virtual 66.8MB)
```

`exited=CODE` matches the exit code. `-s` adds the size of each container's writable layer (and, in brackets, the
"virtual" size including the image).

</details>

## Real-world example

An on-call engineer is told "the nightly import job failed". On the server, `docker ps -a --filter name=import
--filter status=exited -n 5 --format 'table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}'` shows the last five runs and
their exit codes in one screen, before reading any log. Scripts use `-q` with filters, never `grep` on the table, because
the table layout changes between Docker versions.

## Recap

- `docker ps`: running containers; `docker ps -a`: all of them.
- `--filter status=exited` (not "stopped"), `name=`, `ancestor=`, `exited=CODE`.
- `--format` picks columns; `-q` gives IDs for scripts.
- An error that lists valid values tells you the fix: read it fully.

## Cleanup

<!-- test -->
```bash
docker rm -f web job-ok job-failed not-started > /dev/null
```

Next: [Lesson 009 · Container lifecycle](../009-container-lifecycle/README.md)
