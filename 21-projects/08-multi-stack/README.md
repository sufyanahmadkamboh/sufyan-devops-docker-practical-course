# Project 08 · Four stacks behind one proxy

> ⏱ 2 hours · run every command from the course folder

## Goal

Run the course's Go, Python, Node.js and Java APIs side by side, behind one Nginx reverse proxy that routes by path:
`/go/`, `/python/`, `/node/`, `/java/`. One `compose.yaml`, one published port, a healthcheck and resource limits on
every service: the shape of a small platform that hosts several teams' services.

## Requirements

- [ ] Each API has its own Dockerfile (multi-stage for Go and Java), runs as a non-root user and has a healthcheck
- [ ] The proxy starts only when all four APIs are **healthy**, and is the only service with a host port (8088)
- [ ] `GET /<stack>/` and `GET /<stack>/health` reach the right service, with the prefix removed
- [ ] Every service has a CPU and memory limit
- [ ] One service failing does not affect the other three

## Architecture

```text
                                  ┌──▶ go      :8080   Go, static binary on alpine
                                  │
 curl ──▶ :8088 ──▶ proxy ────────┼──▶ python  :8000   Flask + Gunicorn
          nginx, path routing     │
          /go/ /python/ /node/    ├──▶ node    :3000   Node.js 24
          /java/                  │
                                  └──▶ java    :8080   JRE 25
           network project08_default · limits: 0.5 CPU, 256 MB per service
```

## Build it

Four applications from the course's `examples/` (each in its own folder), plus the solution's Dockerfiles, proxy
configuration and Compose file:

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh project-08 examples/go-api examples/python-api examples/node-api examples/java-api
cp -r 21-projects/08-multi-stack/solution/. ~/docker-practice/project-08/
cd ~/docker-practice/project-08
find . -name Dockerfile -o -name compose.yaml -o -name default.conf | sort
```

<!-- test: contains=proxy_pass http://python:8000/; output -->
```bash
cat proxy/default.conf
```

```text
# One entry point, four stacks: the path prefix chooses the service.
# The trailing "/" in proxy_pass replaces the matched prefix: /python/health → http://python:8000/health
server {
  listen 8080;

  location = /healthz {
    access_log off;
    return 200 "ok\n";
  }
  location /go/     { proxy_pass http://go:8080/; }
  location /python/ { proxy_pass http://python:8000/; }
  location /node/   { proxy_pass http://node:3000/; }
  location /java/   { proxy_pass http://java:8080/; }
  location = /      { default_type text/plain; return 200 "try /go/ /python/ /node/ /java/\n"; }
}
```

Build the four images (the first build takes a few minutes: four toolchains), then start:

<!-- test: contains=project08-java; timeout=900 -->
```bash
docker compose build --quiet 2>&1 | tail -3
docker image ls --format '{{.Repository}}:{{.Tag}} {{.Size}}' | grep project08
```

<!-- test: contains=Healthy; timeout=300 -->
```bash
docker compose up -d --wait 2>&1 | tail -2
```

## Verify

Each prefix reaches its own stack:

<!-- test: contains=Hello from Java; contains=Hello from Go; retry=10; output -->
```bash
for stack in go python node java; do
  echo "/$stack/ -> $(curl -s http://localhost:8088/$stack/)"
done
```

```text
/go/ -> {"hostname":"0ab86ddfbd84","message":"Hello from Go"}
/python/ -> {"hostname":"6a245923d356","message":"Hello from Python, behind the proxy"}
/node/ -> {"message":"Hello from Node.js","hostname":"8294df3bbdd3","version":"dev"}
/java/ -> {"message":"Hello from Java","hostname":"5abbe24206ba"}
```

<!-- test: contains=healthy; output -->
```bash
docker compose ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
```

```text
SERVICE   STATUS                   PORTS
go        Up 7 seconds (healthy)   8080/tcp
java      Up 7 seconds (healthy)   8080/tcp
node      Up 7 seconds (healthy)   3000/tcp
proxy     Up 1 second              0.0.0.0:8088->8080/tcp, [::]:8088->8080/tcp
python    Up 7 seconds (healthy)   8000/tcp
```

Users and limits of every service:

<!-- test: contains=268435456; output -->
```bash
for s in go python node java; do
  id=$(docker compose ps -q $s)
  echo "$s: user=$(docker inspect --format '{{.Config.User}}' "$id") memory=$(docker inspect --format '{{.HostConfig.Memory}}' "$id") nano_cpus=$(docker inspect --format '{{.HostConfig.NanoCpus}}' "$id")"
done
```

```text
go: user=65532:65532 memory=268435456 nano_cpus=500000000
python: user=app memory=268435456 nano_cpus=500000000
node: user=node memory=268435456 nano_cpus=500000000
java: user=app memory=268435456 nano_cpus=500000000
```

Stop one service: only its path fails, the other three keep answering.

<!-- test: anyof=/node/ -> 502||/node/ -> 504; contains=/go/ -> 200; output -->
```bash
docker compose stop node 2>&1 | tail -1
for stack in go node; do
  echo "/$stack/ -> $(curl -s -w '\n%{http_code}\n' http://localhost:8088/$stack/ | tail -n 1)"
done
docker compose start node 2>&1 | tail -1
```

```text
 Container project08-node-1 Stopped 
/go/ -> 200
/node/ -> 504
 Container project08-node-1 Started 
```

502 Bad Gateway (or 504 Gateway Timeout, while the proxy still tries the stopped container's old address): the
proxy runs, but nothing answers behind `/node/`. The other routes are not affected.

## Break it and fix it

A small edit to the proxy configuration: someone removes the trailing `/` from the Python route.

<!-- test: contains=404; output -->
```bash
sed -i.bak 's|proxy_pass http://python:8000/;|proxy_pass http://python:8000;|' proxy/default.conf
docker compose exec proxy nginx -s reload 2>&1 | tail -1
sleep 1
curl -s -w '\n/python/ -> %{http_code}\n' http://localhost:8088/python/ | tail -n 1
```

```text
2026/10/05 12:31:04 [notice] 35#35: signal process started
/python/ -> 404
```

The proxy works and Python is healthy, yet Flask answers **404**. Its access log shows which path it received:

<!-- test: contains=/python/; retry=5; output -->
```bash
docker compose logs proxy --no-log-prefix 2>&1 | grep '"GET /python/' | tail -1
docker compose exec python python -c "import app; print(app.app.test_client().get('/python/').status)"
```

```text
172.18.0.1 - - [05/Oct/2026:12:31:05 +0000] "GET /python/ HTTP/1.1" 404 207 "-" "curl/8.19.0" "-"
404 NOT FOUND
```

Without a URI part in `proxy_pass`, Nginx forwards the path unchanged: Flask receives `/python/`, a route it does not
have. With the trailing `/`, Nginx replaces the matched prefix `/python/` with `/`. Restore it and reload (no restart
needed, no connection dropped):

<!-- test: contains=successful -->
```bash
mv proxy/default.conf.bak proxy/default.conf
docker compose exec proxy nginx -t 2>&1 | tail -1
docker compose exec proxy nginx -s reload 2>&1 | tail -1
```

<!-- test: contains=200; retry=5 -->
```bash
curl -s -w '\n/python/ -> %{http_code}\n' http://localhost:8088/python/ | tail -n 1
```

## Stretch goals

- Run two `python` containers (`docker compose up -d --scale python=2`) and show the proxy balancing between them
  (`hostname` in the response). Why does Nginx need `resolver 127.0.0.11` and a variable in `proxy_pass` to notice a
  new container (the capstone's proxy does this)?
- Put the four APIs on a `backend` network marked `internal` and the proxy on both networks.
- Add `read_only: true`, `tmpfs` and `cap_drop: [ALL]` to every service and prove they still pass their healthchecks.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/project-08
docker compose down -v 2>&1 | tail -1
docker image rm -f project08-go:1.0 project08-python:1.0 project08-node:1.0 project08-java:1.0 > /dev/null
cd ~ && rm -rf ~/docker-practice/project-08
```

Next: [All projects](../README.md)
