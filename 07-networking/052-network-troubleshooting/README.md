# Lesson 052 · Network troubleshooting

> Level 8 · Networking · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

"I can't reach my container" has a short list of causes, and each one has a command that proves or rules it out. Work
from the outside in: is the container running, is the port published, is the application listening on the right port,
is it listening on the right **address**, are client and server on the same network, is the name right? The classic
trap is an application listening on `127.0.0.1` inside its container: it works from inside, and nothing else can reach
it.

## Visual

```text
  client ──▶ [1] container running? ──▶ [2] port published? ──▶ [3] app listening on that container port?
                docker ps                  docker port              netstat -tln (in the container's namespace)
                                                                          │
         ┌────────────────────────────────────────────────────────────────┘
         ▼
     [4] listening on 0.0.0.0, not 127.0.0.1? ──▶ [5] same network? ──▶ [6] right name?
          netstat: 0.0.0.0:8000 ✔                   docker inspect          nslookup NAME
                   127.0.0.1:8000 ✘ (only reachable  …Networks
                   from inside the container)

  127.0.0.1 inside a container = that container only, never the host and never other containers
```

| Symptom | Likely cause | Proof |
|---|---|---|
| `Connection refused` (curl exit 7) on the host | port not published, or wrong host port | `docker port C` |
| `Empty reply` / `Connection reset` (exit 52/56) | published, but the app listens on another port or on `127.0.0.1` | `netstat -tln` in the container's namespace |
| `bad address` / `Could not resolve host` | wrong name, or not on the same network | `nslookup NAME`, `docker inspect … Networks` |
| request hangs, then times out | a firewall, or a dependency that hangs (lesson 049) | test the dependency from inside the container |

## Lab setup

A web server listening on `127.0.0.1:8000` inside its container (a common default of development servers), published
on host port 8080:

<!-- test: contains=app -->
```bash
docker network create debug-net > /dev/null
docker run -d --name app --network debug-net -p 8080:8000 python:3.14-slim python -m http.server 8000 --bind 127.0.0.1 > /dev/null
docker ps --filter name=app --format '{{.Names}}: {{.Status}}, {{.Ports}}'
```

## Demonstration

From inside the container, the server works:

<!-- test: contains=200; output; retry=5 -->
```bash
docker exec app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000').status)"
```

```text
200
```

## Command breakdown

| Command | What it proves |
|---|---|
| `docker ps --filter name=C` | the container runs (and has not exited) |
| `docker port C` | which host ports forward to which container ports |
| `docker run --rm --network container:C busybox:1.37 netstat -tln` | the listening sockets **inside** C, with tools C does not have |
| `docker inspect C --format '{{range $n, $_ := .NetworkSettings.Networks}}{{$n}} {{end}}'` | C's networks |
| `docker run --rm --network NET busybox:1.37 nslookup NAME` | whether NAME resolves on NET |

## Hands-on lab

**Instructions.** Run steps 1 and 2 of the checklist for `app`: show that it is running and that its port is
published.

**Expected result.** `Up …`, and `8000/tcp -> 0.0.0.0:8080`.

**Verification.**

<!-- test: contains=Up; contains=8000/tcp -->
```bash
docker ps --filter name=app --format '{{.Status}}'
docker port app
```

## Break it

Now call it from the host, the way a user would:

<!-- test: fail; anyof=curl exit code 52||curl exit code 56; output -->
```bash
code=0; curl -s -m 5 http://localhost:8080 > /dev/null || code=$?
echo "curl exit code $code"
[ "$code" -eq 0 ]
```

```text
curl exit code 52
```

And from another container on the same network:

<!-- test: fail; anyof=refused||can't connect; output -->
```bash
docker run --rm --network debug-net busybox:1.37 wget -qO /dev/null -T 5 http://app:8000 2>&1
```

```text
wget: can't connect to remote host (172.18.0.2): Connection refused
```

## Troubleshoot it

Steps 1 and 2 passed: running and published. The host gets an empty reply (Docker accepted the connection on 8080
but nothing answered on the container side), and another container is refused. Step 3 and 4: what is listening inside
the container? The image has no `netstat`, so borrow BusyBox's, in the **same network namespace** as `app`:

<!-- test: contains=127.0.0.1:8000; output -->
```bash
docker run --rm --network container:app busybox:1.37 netstat -tln
```

```text
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       
tcp        0      0 127.0.0.11:41811        0.0.0.0:*               LISTEN      
tcp        0      0 127.0.0.1:8000          0.0.0.0:*               LISTEN      
```

(The `127.0.0.11:…` line is Docker's embedded DNS server, lesson 050.) `127.0.0.1:8000`: the server listens on the container's loopback interface only. Traffic forwarded from the host and
from other containers arrives on `eth0`, where nothing listens. The port is right; the **address** is wrong.

## Fix it

Make the application listen on all interfaces, `0.0.0.0` (for this server `--bind 0.0.0.0`; for Flask
`--host 0.0.0.0`, for Node `server.listen(port, "0.0.0.0")`), and recreate the container:

<!-- test: contains=from the host: 200; contains=from a container: ok; output; retry=5 -->
```bash
docker rm -f app > /dev/null
docker run -d --name app --network debug-net -p 8080:8000 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
docker run --rm --network container:app busybox:1.37 netstat -tln | grep 8000
echo "from the host: $(curl -s -w '\n%{http_code}' http://localhost:8080 | tail -1)"
docker run --rm --network debug-net busybox:1.37 wget -qO /dev/null -T 5 http://app:8000 && echo "from a container: ok"
```

```text
tcp        0      0 0.0.0.0:8000            0.0.0.0:*               LISTEN      
from the host: 200
from a container: ok
```

## Practice challenge

A colleague starts the fixed server with `-p 8081:80` because "web servers use port 80". Reproduce it, prove with the
checklist which step fails, and fix it.

<details>
<summary>Solution</summary>

<!-- test: contains=published: 80/tcp; contains=listening: ; contains=fixed: 200; output; retry=5 -->
```bash
docker run -d --name app2 -p 8081:80 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
echo "published: $(docker port app2)"
echo "listening: $(docker run --rm --network container:app2 busybox:1.37 netstat -tln | grep -o '0.0.0.0:8000')"
docker rm -f app2 > /dev/null
docker run -d --name app2 -p 8081:8000 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
echo "fixed: $(curl -s -w '\n%{http_code}' http://localhost:8081 | tail -1)"
```

```text
published: 80/tcp -> 0.0.0.0:8081
80/tcp -> [::]:8081
listening: 0.0.0.0:8000
fixed: 200
```

Step 3 fails: the host port forwards to container port 80, but the application listens on 8000. The container port
in `-p HOST:CONTAINER` must be the port the application really listens on.

</details>

## Real-world example

A team containerizes a Flask service. It works with `docker exec … curl localhost:5000`, yet the load balancer marks
it down. `netstat` in the container's namespace shows `127.0.0.1:5000`: `flask run` binds to localhost by default.
Changing the start command to `gunicorn -b 0.0.0.0:5000 app:app` fixes it, and the team adds the check
"listens on 0.0.0.0" to its Dockerfile review list.

## Recap

- Troubleshoot from the outside in: running → published → listening port → listening address → network → name.
- `127.0.0.1` inside a container means only that container; servers in containers must listen on `0.0.0.0`.
- `--network container:NAME` runs a debugging tool in another container's network namespace.
- `-p HOST:CONTAINER`: the container port must be the application's real listening port.

## Cleanup

<!-- test -->
```bash
docker rm -f app app2 > /dev/null
docker network rm debug-net > /dev/null
```

Next: [Lesson 053 · The container's writable layer](../../08-storage/053-writable-layer/README.md)
