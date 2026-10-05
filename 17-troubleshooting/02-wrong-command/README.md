# Troubleshooting problem 02 · Wrong command

> ⏱ 15 minutes · run every command from the course folder · related lessons: 009, 027, 028, 029

## Problem

A new image of the orders service never starts. `docker run` fails at once, and the container appears in
`docker ps -a` as `Created`, never `Up`.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-02 17-troubleshooting/02-wrong-command/examples
cd ~/docker-practice/trouble-02
docker build -q -t orders:broken broken > /dev/null
```

<!-- test: fail; contains=executable file not found; output -->
```bash
docker run -d --name orders -p 8080:8080 orders:broken 2>&1
```

```text
424779f01acc4a8f239359734dc417e4affefd2626e1422e853f8d120c0e7f4b
docker: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "pyhton": executable file not found in $PATH

Run 'docker run --help' for more information
```

<!-- test: contains=Created; output -->
```bash
docker ps -a --filter name=orders --format '{{.Names}}: {{.Status}}'
```

```text
orders: Created
```

## Investigation

**1. Read the error from the end.** The useful part is the last clause: `exec: "pyhton": executable file not found in
$PATH`. Docker created the container, then runc tried to start its process and could not find the program.

**2. The exit code and error are stored in the container:**

<!-- test: contains=127; output -->
```bash
docker inspect --format 'exit code {{.State.ExitCode}}' orders
```

```text
exit code 127
```

**3. Which command was configured?**

<!-- test: contains=pyhton; output -->
```bash
docker image inspect --format 'Entrypoint: {{.Config.Entrypoint}}  Cmd: {{.Config.Cmd}}' orders:broken
```

```text
Entrypoint: []  Cmd: [pyhton app.py]
```

**4. Does the program exist in the image?** Override the command to look:

<!-- test: contains=pyhton: not found; output -->
```bash
docker run --rm orders:broken sh -c 'for p in python pyhton; do command -v $p > /dev/null && echo "$p: $(command -v $p)" || echo "$p: not found"; done'
```

```text
python: /usr/local/bin/python
pyhton: not found
```

`python` exists; `pyhton` does not.

## Commands

| Command | What it tells you |
|---|---|
| `docker ps -a` | `Created` = the process never started; `Exited (127)` = it started a shell that could not find a command |
| `docker inspect --format '{{.State.ExitCode}} {{.State.Error}}' NAME` | the stored exit code and runtime error |
| `docker image inspect --format '{{.Config.Cmd}}' IMAGE` | the default command baked into the image |
| `docker run --rm IMAGE sh -c 'command -v PROGRAM'` | whether a program exists on the image's `PATH` |

## Output interpretation

| Exit code | Meaning |
|---|---|
| 125 | `docker run` itself failed (bad flag, port in use: [problem 04](../04-port-already-in-use/README.md)) |
| 126 | the command exists but cannot be executed (not executable, wrong format) |
| 127 | the command was not found (typo, not installed, not on `PATH`, wrong image) |

`executable file not found in $PATH` with the **exec form** (`CMD ["…"]`) means the first element of the array is
looked up directly. With the shell form (`CMD pyhton app.py`) the container would start `/bin/sh` instead and exit
with `Exited (127)` and a `pyhton: not found` message from the shell in its logs.

## Root cause

A typo in the Dockerfile: `CMD ["pyhton", "app.py"]`. The program `pyhton` does not exist in the image.

## Fix

<!-- test: contains=python; output -->
```bash
grep CMD broken/Dockerfile fixed/Dockerfile
```

```text
broken/Dockerfile:CMD ["pyhton", "app.py"]
fixed/Dockerfile:CMD ["python", "app.py"]
```

<!-- test -->
```bash
docker rm orders > /dev/null
docker build -q -t orders:fixed fixed > /dev/null
docker run -d --name orders -p 8080:8080 orders:fixed > /dev/null
```

## Verification

<!-- test: retry=10; contains=orders service ok; output -->
```bash
curl -s http://localhost:8080
```

```text
orders service ok
```

## Prevention

- Run the image once locally (or in CI) before pushing it: `docker run --rm IMAGE` catches this in seconds.
- Use the exec form (`CMD ["python", "app.py"]`): the error is explicit and signals reach the process (lesson 027).
- Add a smoke test to the pipeline: start the container and call its health endpoint (lesson 135).

## Cleanup

<!-- test -->
```bash
docker rm -f orders > /dev/null
docker image rm orders:broken orders:fixed > /dev/null
rm -rf ~/docker-practice/trouble-02
```

Next: [Problem 03 · Wrong image](../03-wrong-image/README.md)
