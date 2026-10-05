# Lesson 011 · Running Nginx

> Level 3 · Working with containers · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

So far our containers ran a command and exited. A **server** container keeps running: its main process (here the Nginx
web server) waits for requests until it is stopped. We run one in the background with `-d`, check that it serves pages,
and discover the first rule of container networking: a server inside a container is **not** reachable from your computer
until you publish its port.

## Visual

```text
 Your computer                                Docker engine
 ┌──────────────────────────┐                 ┌───────────────────────────────────────────────┐
 │ curl localhost:8080  ──X │  nothing is     │  container "web"   (IP 172.17.0.2 on the     │
 │                          │  published      │                     internal bridge network)  │
 │                          │                 │   nginx  listening on port 80                 │
 └──────────────────────────┘                 │      ▲                                        │
                                              │      │ http://172.17.0.2:80  ✓ (from another  │
                                              │  container "client" ───────    container)     │
                                              └───────────────────────────────────────────────┘
  80/tcp in `docker ps` = the port the image declares, NOT a port open on your computer.
  -p 8080:80 publishes it (next lesson).
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-011 examples/site
cd ~/docker-practice/lesson-011
ls
```

A two-file static website: `index.html` and `styles.css`.

## Demonstration

Start Nginx in the background (`-d`, detached):

<!-- test: contains=web; output -->
```bash
docker run -d --name web nginx:1.30-alpine
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

```text
578f683ddd7839ca4104bac29b5d1ac78a2afb28f116f2d0402021747de89f66
NAMES     STATUS                  PORTS
web       Up Less than a second   80/tcp
```

`docker run -d` prints the new container's ID and returns at once; Nginx keeps running. Its startup messages are in the
container's log (lesson 014):

<!-- test: contains=start worker process; output=tail:3 -->
```bash
docker logs web 2>&1
```

```text
...
2026/10/05 10:48:31 [notice] 1#1: start worker process 41
2026/10/05 10:48:31 [notice] 1#1: start worker process 42
2026/10/05 10:48:31 [notice] 1#1: start worker process 43
```

Is it serving? Ask from **another container**: containers on the same Docker network can reach each other's ports:

<!-- test: contains=Welcome to nginx!; retry=10; output -->
```bash
ip=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web)
echo "web has the IP address $ip"
docker run --rm alpine:3.23 wget -qO- "http://$ip" | grep '<title>'
```

```text
web has the IP address 172.17.0.2
<title>Welcome to nginx!</title>
```

Replace the default page with the lab's website. `docker cp` copies files into a container, running or not:

<!-- test: contains=Welcome to the cafe; output -->
```bash
docker cp index.html web:/usr/share/nginx/html/index.html
docker cp styles.css web:/usr/share/nginx/html/styles.css
docker run --rm alpine:3.23 wget -qO- "http://$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web)" | grep '<h1>'
```

```text
  <h1>Welcome to the cafe</h1>
```

Files copied into a container live in its writable layer: a new container from the image would show the default page
again. Lesson 022 builds an image that contains the website, and lesson 054 mounts it from your computer instead.

## Command breakdown

| Command / part | Meaning |
|---|---|
| `docker run -d` | run in the background and print the container ID |
| `nginx:1.30-alpine` | the official Nginx image, version 1.30, on Alpine Linux |
| `80/tcp` in PORTS | a port the image **declares** (`EXPOSE`, lesson 032), not published |
| `--format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'` | the container's IP address on its networks |
| `wget -qO- URL` | download URL and print it (BusyBox `wget` in Alpine) |
| `docker cp FILE NAME:PATH` | copy a file into a container |

## Hands-on lab

**Instructions.** Start a second Nginx container named `web-2` from the image `nginx:1.29-alpine` (an older version) and
ask it for its version from another container. Nginx sends its version in the `Server` response header.

**Expected result.** `Server: nginx/1.29…` for `web-2`.

**Verification.**

<!-- test: contains=nginx/1.29; retry=10 -->
```bash
docker run -d --name web-2 nginx:1.29-alpine > /dev/null 2>&1 || true
docker run --rm alpine:3.23 wget -qS -O /dev/null "http://$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' web-2)" 2>&1 | grep Server
```

## Break it

Open the website from your own computer:

<!-- test: fail; anyof=Failed to connect||Couldn't connect||Empty reply; output -->
```bash
curl -sS http://localhost:8080
```

```text
curl: (7) Failed to connect to localhost port 8080 after 2232 ms: Could not connect to server
```

## Troubleshoot it

The server works (other containers get the page), but nothing on your computer listens on port 8080: `curl` gets no
connection (`Failed to connect … Couldn't connect to server`; with Docker Desktop on Windows it can also be
`Empty reply from server`). Look at the PORTS column:

<!-- test: contains=80/tcp; absent=0.0.0.0 -->
```bash
docker ps --filter name=^web$ --format '{{.Names}}: {{.Ports}}'
```

`80/tcp` without an arrow means "the image says it uses port 80", nothing more. A published port looks like
`0.0.0.0:8080->80/tcp`. The container's network is internal to Docker; you have to publish a port explicitly.

## Fix it

A container's ports are fixed when it is created, so replace it with one that publishes port 80 as 8080 on your
computer (next lesson in detail), and copy the website again:

<!-- test: contains=0.0.0.0:8080->80/tcp -->
```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 nginx:1.30-alpine > /dev/null
docker cp index.html web:/usr/share/nginx/html/index.html
docker cp styles.css web:/usr/share/nginx/html/styles.css
docker ps --filter name=^web$ --format '{{.Names}}: {{.Ports}}'
```

<!-- test: contains=Welcome to the cafe; retry=10 -->
```bash
curl -s http://localhost:8080 | grep '<h1>'
```

Open <http://localhost:8080> in your browser too.

## Practice challenge

Check that Nginx serves `styles.css` with the right content type. Then stop `web`, start it again, and check whether the
website is still there. Explain the result.

<details>
<summary>Solution</summary>

<!-- test: contains=text/css; output -->
```bash
curl -sI http://localhost:8080/styles.css | grep -i '^content-type'
```

```text
Content-Type: text/css
```

<!-- test: contains=Welcome to the cafe; retry=10; output -->
```bash
docker stop web > /dev/null && docker start web > /dev/null
curl -s http://localhost:8080 | grep '<h1>'
```

```text
  <h1>Welcome to the cafe</h1>
```

The website survives stop and start: the files are in the container's writable layer, which lives as long as the
container. Only removing the container (or creating a new one) loses them.

</details>

## Real-world example

Nginx in a container is one of the most common building blocks: a static frontend, a reverse proxy in front of APIs
(the capstone uses one), or a TLS terminator. In production nobody copies files into a running container: the website
is built into an image (lesson 022) so that every container from it is identical, and ports are published by the
deployment (Compose, Kubernetes) rather than typed by hand.

## Recap

- `docker run -d` runs a server container in the background.
- `80/tcp` in `docker ps` is a declared port, not a published one: the host cannot reach it.
- Other containers can reach it by IP on Docker's network.
- Ports are set at creation: publish with `-p HOST:CONTAINER` (lesson 012).

## Cleanup

<!-- test -->
```bash
docker rm -f web web-2 > /dev/null
rm -rf ~/docker-practice/lesson-011
```

Next: [Lesson 012 · Port mapping](../012-port-mapping/README.md)
