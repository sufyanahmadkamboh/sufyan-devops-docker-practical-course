# Troubleshooting problem 06 · Application listening on localhost

> ⏱ 15 minutes · run every command from the course folder · related lessons: 012, 046, 052

## Problem

The tickets service works on the developer's laptop with `python app.py`. In a container, with the port published
correctly, every request from the host fails with an empty reply.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-06 17-troubleshooting/06-listening-on-localhost/examples
cd ~/docker-practice/trouble-06
docker run -d --name tickets -p 8080:8080 -v "$(pwd)/broken:/app" -w /app python:3.14-slim python app.py > /dev/null
```

<!-- test: fail; anyof=curl: (52)||curl: (56); output -->
```bash
sleep 2
curl -sS http://localhost:8080 2>&1
```

```text
curl: (52) Empty reply from server
```

## Investigation

**1. Running and published?** Both look right:

<!-- test: contains=8080->8080; output -->
```bash
docker ps --filter name=tickets --format '{{.Names}}: {{.Status}}  {{.Ports}}'
```

```text
tickets: Up 2 seconds  0.0.0.0:8080->8080/tcp, [::]:8080->8080/tcp
```

**2. Does it answer inside the container?**

<!-- test: contains=tickets service ok; output -->
```bash
docker exec tickets python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8080').read().decode())"
```

```text
tickets service ok
```

So the application works, but only from inside. **3. Which address does it listen on?** The `python:3.14-slim` image
has no `netstat` or `ss`, so borrow them: a BusyBox container that joins the same network namespace
(`--network container:NAME`) sees exactly the same sockets:

<!-- test: contains=127.0.0.1:8080; output -->
```bash
docker run --rm --network container:tickets busybox:1.37 netstat -tln
```

```text
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       
tcp        0      0 127.0.0.1:8080          0.0.0.0:*               LISTEN      
```

## Commands

| Command | What it tells you |
|---|---|
| `docker exec NAME …` request to `localhost` | whether the app answers inside the container |
| `docker run --rm --network container:NAME busybox:1.37 netstat -tln` | the listening sockets of that container, without installing tools in it |
| `docker ps --format '{{.Ports}}'` | that the port is published (so this is not [problem 05](../05-application-not-reachable/README.md)) |

## Output interpretation

`127.0.0.1:8080` means the server accepts connections on the container's **loopback** interface only. A published port
forwards traffic to the container's network interface (`eth0`, an address like `172.17.0.2`), where nothing listens:
Docker's port forwarder accepts the connection from `curl`, cannot reach the application, and closes it, which `curl`
reports as `(52) Empty reply from server` (or `(56) Connection reset` on some systems). `0.0.0.0:8080` would mean
"every interface", and the forwarded traffic would arrive.

## Root cause

The application binds to `127.0.0.1`. That is fine on a laptop, where the browser runs on the same machine, but inside a
container "localhost" is the container itself.

## Fix

Bind to `0.0.0.0` (all interfaces). Many frameworks have the same default and a flag or variable for it: Flask
`--host 0.0.0.0`, `uvicorn --host 0.0.0.0`, Node `server.listen(port, '0.0.0.0')`, Spring Boot `server.address`.

<!-- test: contains=0.0.0.0; output -->
```bash
grep -h "HTTPServer((" broken/app.py fixed/app.py
```

```text
HTTPServer(("127.0.0.1", 8080), Tickets).serve_forever()
HTTPServer(("0.0.0.0", 8080), Tickets).serve_forever()
```

<!-- test -->
```bash
docker rm -f tickets > /dev/null
docker run -d --name tickets -p 8080:8080 -v "$(pwd)/fixed:/app" -w /app python:3.14-slim python app.py > /dev/null
```

## Verification

<!-- test: retry=10; contains=tickets service ok; output -->
```bash
curl -s http://localhost:8080
```

```text
tickets service ok
```

<!-- test: contains=0.0.0.0:8080; output -->
```bash
docker run --rm --network container:tickets busybox:1.37 netstat -tln
```

```text
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       
tcp        0      0 0.0.0.0:8080            0.0.0.0:*               LISTEN      
```

## Prevention

- Make the listen address configurable and default it to `0.0.0.0` in the image (for example `ENV HOST=0.0.0.0`).
- Publish to `127.0.0.1` on the **host** side (`-p 127.0.0.1:8080:8080`) when you want to restrict access, never by
  binding the app to loopback inside the container (lesson 051).
- Keep the `--network container:NAME` trick: it debugs networking of minimal images without changing them.

## Cleanup

<!-- test -->
```bash
docker rm -f tickets > /dev/null
rm -rf ~/docker-practice/trouble-06
```

Next: [Problem 07 · Wrong container port](../07-wrong-container-port/README.md)
