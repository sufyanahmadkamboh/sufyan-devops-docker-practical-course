# Lesson 054 · Bind mounts

> Level 9 · Storage · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A **bind mount** makes a file or folder of the host appear at a path inside the container. Both sides see the same
files: change one on the host and the container sees it immediately. That makes bind mounts the tool for development
(edit code on your laptop, run it in a container) and for handing configuration files to a container. The host path
must be **absolute**: a bare name such as `site` means something else entirely (a named volume).

## Visual

```text
  host: ~/docker-practice/lesson-054/site/        container: /usr/share/nginx/html/
 ┌───────────────────────────────┐   bind mount   ┌───────────────────────────────┐
 │ index.html   styles.css       │◀══════════════▶│ index.html   styles.css       │
 └───────────────────────────────┘  same files    └───────────────────────────────┘
  edit on the host → visible in the container at once       :ro → the container cannot write

  -v "$(pwd)/site:/usr/share/nginx/html"     absolute host path → bind mount ✔
  -v site:/usr/share/nginx/html              a bare name       → named volume "site" ✘ (not your folder)
  --mount type=bind,source="$(pwd)/site",target=/usr/share/nginx/html,readonly    explicit form
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-054 examples/site
cd ~/docker-practice/lesson-054
mkdir site && mv index.html styles.css site/
ls site
```

## Demonstration

Serve the folder with nginx, read-only:

<!-- test: contains=Welcome to the cafe; output; retry=5 -->
```bash
docker run -d --name site -p 8080:80 -v "$(pwd)/site:/usr/share/nginx/html:ro" nginx:1.30-alpine > /dev/null
curl -s http://localhost:8080 | grep -o '<h1>.*</h1>'
```

```text
<h1>Welcome to the cafe</h1>
```

Change the page on the host. No rebuild, no restart:

<!-- test: contains=Now open on Sundays; output; retry=5 -->
```bash
sed -i.bak 's|<h1>Welcome to the cafe</h1>|<h1>Welcome to the cafe</h1><p>Now open on Sundays</p>|' site/index.html && rm site/index.html.bak
curl -s http://localhost:8080 | grep -o '<p>Now open on Sundays</p>'
```

```text
<p>Now open on Sundays</p>
```

`docker inspect` shows the mount: its type, source on the host, destination and mode:

<!-- test: contains=bind; output -->
```bash
docker inspect site --format '{{range .Mounts}}{{.Type}} {{.Destination}} rw={{.RW}}{{end}}'
```

```text
bind /usr/share/nginx/html rw=false
```

## Command breakdown

| Form | Meaning |
|---|---|
| `-v /abs/host/path:/container/path` | bind mount (short form); the host path must be absolute |
| `-v "$(pwd)/site:/path:ro"` | read-only: the container cannot change the files |
| `--mount type=bind,source=…,target=…[,readonly]` | the explicit form: fails if the source does not exist |
| `docker inspect C --format '{{range .Mounts}}…{{end}}'` | the container's mounts |

A bind mount **hides** whatever the image had at the target path: here nginx's default page is invisible while the
mount is in place.

## Hands-on lab

**Instructions.** Prove that the mount is read-only: try to create a file in `/usr/share/nginx/html` from inside the
container.

**Expected result.** `Read-only file system`.

**Verification.**

<!-- test: contains=Read-only file system -->
```bash
docker exec site sh -c 'touch /usr/share/nginx/html/hacked.html' 2>&1 || true
```

## Break it

A teammate copies the command but writes the folder as a relative name:

<!-- test: contains=Welcome to nginx; output; retry=5 -->
```bash
docker run -d --name site2 -p 8081:80 -v site:/usr/share/nginx/html nginx:1.30-alpine > /dev/null
curl -s http://localhost:8081 | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

The container runs, but it serves nginx's default page instead of the cafe.

## Troubleshoot it

When a container does not see your files, inspect its mounts:

<!-- test: contains=volume; output -->
```bash
docker inspect site2 --format '{{range .Mounts}}{{.Type}} name={{.Name}} -> {{.Destination}}{{end}}'
docker volume ls --filter name=^site$
```

```text
volume name=site -> /usr/share/nginx/html
DRIVER    VOLUME NAME
local     site
```

`volume name=site`: a source without a `/` is the name of a **named volume**. Docker created an empty volume called
`site` and, because it was empty, copied the image's files (nginx's default page) into it. Your folder was never
involved.

## Fix it

Use an absolute path (`"$(pwd)/site"`), or the `--mount` form, which says explicitly what it is and refuses a source
that does not exist:

<!-- test: contains=Welcome to the cafe; output; retry=5 -->
```bash
docker rm -f site2 > /dev/null
docker volume rm site > /dev/null
docker run -d --name site2 -p 8081:80 --mount type=bind,source="$(pwd)/site",target=/usr/share/nginx/html,readonly nginx:1.30-alpine > /dev/null
curl -s http://localhost:8081 | grep -o '<h1>.*</h1>'
```

```text
<h1>Welcome to the cafe</h1>
```

## Practice challenge

Override a single **file** instead of a folder: write your own `nginx.conf` server block on the host that returns the
text `hello from my config` on every request, and bind-mount it over `/etc/nginx/conf.d/default.conf`.

<details>
<summary>Solution</summary>

<!-- test: contains=hello from my config; output; retry=5 -->
```bash
cd ~/docker-practice/lesson-054
printf 'server {\n  listen 80;\n  location / { return 200 "hello from my config\\n"; }\n}\n' > default.conf
docker run -d --name custom -p 8082:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
curl -s http://localhost:8082
```

```text
hello from my config
```

Mounting single configuration files is how many teams configure off-the-shelf images without building their own.

</details>

## Real-world example

During development, a team runs its API in a container with the source folder bind-mounted and a file watcher that
restarts the server on changes: they edit code in their editor, and the container runs it with the production runtime
and libraries. In production, they never bind-mount code: the code is baked into the image, and bind mounts are used
only for a few read-only configuration files, if at all.

## Recap

- A bind mount shares a host file or folder with the container; changes are visible on both sides at once.
- The host path must be absolute (`"$(pwd)/…"`); a bare name creates a named volume instead.
- Add `:ro` (or `readonly`) unless the container must write; a mount hides the image's files at the target path.
- `docker inspect … .Mounts` shows the type, source and destination of every mount.

## Cleanup

<!-- test -->
```bash
docker rm -f site site2 custom > /dev/null
rm -rf ~/docker-practice/lesson-054
```

Next: [Lesson 055 · Named volumes](../055-named-volumes/README.md)
