# Lesson 132 · Immutable containers

> Level 19 · Production · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

An **immutable** container is never changed after it starts. No `docker exec` to edit a file, no package installed
by hand, no "quick fix" on the server. Every change is a new image, with a new tag, that replaces the old container.
That way the image *is* the version: what runs is exactly what was built, tested and recorded, and going back is
starting the previous image.

## Visual

```text
 Mutable (patching a running container)              Immutable (replace with a new image)

 site:1.0 ──run──▶ container ──exec: edit file──▶ ?  site:1.0 ──run──▶ container v1.0
                        │                                 │
                  nobody knows what runs                  │ change → build → test
                  lost on the next rm / restart           ▼
                  not in Git, not in any image      site:1.1 ──run──▶ container v1.1  (v1.0 removed)
                                                          rollback: run site:1.0 again
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-132 examples/site
cp 18-production/132-immutable-containers/examples/Dockerfile ~/docker-practice/lesson-132/
cd ~/docker-practice/lesson-132
docker build -q -t site:1.0 . > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
```

## Demonstration

The site runs from image `site:1.0`:

<!-- test: retry=10; contains=Welcome to the cafe; output -->
```bash
curl -s http://localhost:8080/ | grep "<h1>"
```

```text
  <h1>Welcome to the cafe</h1>
```

`docker diff` lists every file that changed in the container since it started from its image. Right now, only the
image's own startup script and Nginx have been at work: the startup script adjusted `default.conf` (it enables
IPv6), and Nginx created its PID file and cache directories:

<!-- test: absent=index.html; output -->
```bash
docker diff site
```

```text
C /run
A /run/nginx.pid
C /etc
C /etc/nginx
C /etc/nginx/conf.d
C /etc/nginx/conf.d/default.conf
C /var
C /var/cache
C /var/cache/nginx
A /var/cache/nginx/client_temp
A /var/cache/nginx/fastcgi_temp
A /var/cache/nginx/proxy_temp
A /var/cache/nginx/scgi_temp
A /var/cache/nginx/uwsgi_temp
```

(`C` = changed, `A` = added, `D` = deleted.) The website's own files are unchanged: the content is exactly the image's.

## Command breakdown

| Command | What it does |
|---|---|
| `docker diff NAME` | files added (`A`), changed (`C`) or deleted (`D`) in the container's writable layer |
| `docker build -t site:1.1 .` | a new version is a new image with a new tag |
| `docker rm -f site` + `docker run … site:1.1` | deploy = replace the container, never edit it |
| `docker run … site:1.0` | rollback = start the previous image again |

## Hands-on lab

**Instructions.** Show which image the running container was started from, and its image ID.

**Expected result.** `site:1.0` and a `sha256:` ID: the exact version that is running.

**Verification.**

<!-- test: contains=site:1.0 sha256: -->
```bash
docker inspect site --format '{{.Config.Image}} {{.Image}}'
```

## Break it

The marketing team needs a new headline *now*, so someone edits the page inside the running container:

<!-- test: contains=Now with breakfast -->
```bash
docker exec site sed -i 's|Welcome to the cafe|Now with breakfast|' /usr/share/nginx/html/index.html
curl -s http://localhost:8080/ | grep "<h1>"
```

It works. A week later, the container is recreated (a host restart with a new container, a deployment, a scaling
event), from the image:

<!-- test: retry=10; contains=Welcome to the cafe; output -->
```bash
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
```

```text
  <h1>Welcome to the cafe</h1>
```

The headline is gone, and nobody knows why.

## Troubleshoot it

The edit lived only in the old container's writable layer. Before removing a container, `docker diff` shows such hand
changes, which is why it is the first command to run on a container you suspect has been "patched". Reproduce the
edit and look:

<!-- test: contains=index.html; output -->
```bash
docker exec site sed -i 's|Welcome to the cafe|Now with breakfast|' /usr/share/nginx/html/index.html
docker diff site | grep html
```

```text
C /usr/share/nginx/html
C /usr/share/nginx/html/index.html
```

`C /usr/share/nginx/html/index.html`: the running container no longer matches its image `site:1.0`. The change is not in
Git, not in any image, not reviewed and not tested, and it disappears with the container.

## Fix it

Make the change where it belongs: in the source, then build a **new version** and replace the container.

<!-- test: retry=10; contains=Now with breakfast; output -->
```bash
cd ~/docker-practice/lesson-132
sed 's|Welcome to the cafe|Now with breakfast|' index.html > index.new && mv index.new index.html
docker build -q -t site:1.1 . > /dev/null
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.1 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
docker diff site | grep -c html || true
```

```text
  <h1>Now with breakfast</h1>
0
```

The new headline survives any number of restarts, and `docker diff` finds no hand changes (`0`): the container is
exactly `site:1.1`.

## Practice challenge

Version 1.1 has a problem: roll back to version 1.0 and prove the old headline is back, without building anything.

<details>
<summary>Solution</summary>

<!-- test: retry=10; contains=Welcome to the cafe; output -->
```bash
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
```

```text
  <h1>Welcome to the cafe</h1>
```

Because every version is a separate, unchanged image, a rollback is starting the previous one: seconds, and exactly
the bytes that ran before.

</details>

## Real-world example

During an incident, an engineer fixes a configuration file inside a production container with `docker exec`. The
service recovers, the incident is closed, and the fix is lost at the next deployment, so the incident happens again.
Teams that run immutable containers forbid this: production containers often run with a read-only file system
(lesson 084) so that hand edits are impossible, and every fix goes through a commit, a build and a deployment, which
also leaves a record of what changed and why.

## Recap

- Never change a running container; build a new image with a new tag and replace the container.
- `docker diff` shows files changed inside a container since it started.
- Hand changes are lost when the container is recreated, and are in no image, no Git history.
- Rollback = run the previous image tag.

## Cleanup

<!-- test -->
```bash
docker rm -f site > /dev/null
docker image rm -f site:1.0 site:1.1 > /dev/null
rm -rf ~/docker-practice/lesson-132
```

Next: [Lesson 133 · Production configuration](../133-production-configuration/README.md)
