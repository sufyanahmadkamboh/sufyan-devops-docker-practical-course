# Lesson 015 · Running commands in containers (exec)

> Level 3 · Working with containers · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`docker exec` starts an **additional** process inside a **running** container: it shares the container's file system,
network and environment. It is the tool for looking inside: read a configuration file, check what the application sees,
test a connection from the container's point of view, or open an interactive shell. It does not restart or change the
main process, and whatever you change by hand is lost when the container is replaced.

## Visual

```text
  container "web" (running)
  ┌─────────────────────────────────────────────────────────┐
  │ PID 1   nginx: master process      ← the main process   │
  │ PID 30  nginx: worker process                           │
  │ PID 45  cat /etc/nginx/nginx.conf  ← docker exec web cat …  (ends, container keeps running)
  │ PID 52  sh                         ← docker exec -it web sh  (interactive, until you type exit)
  └─────────────────────────────────────────────────────────┘
  same files · same network · same environment variables · needs the container to be running
```

## Lab setup

<!-- test: contains=web -->
```bash
docker run -d --name web -p 8080:80 -e SHOP_MODE=demo nginx:1.30-alpine
docker ps --format '{{.Names}}: {{.Status}}'
```

## Demonstration

Run single commands inside the container:

<!-- test: contains=nginx version; contains=Alpine; output -->
```bash
docker exec web nginx -v 2>&1
docker exec web cat /etc/alpine-release | sed 's/^/Alpine /'
```

```text
nginx version: nginx/1.30.5
Alpine 3.24.2
```

The container's processes, seen from inside: the main process is PID 1, and `ps` itself appears because `exec` added
it:

<!-- test: contains=nginx: master process; output -->
```bash
docker exec web ps -o pid,user,args
```

```text
PID   USER     COMMAND
    1 root     nginx: master process nginx -g daemon off;
   30 nginx    nginx: worker process
   31 nginx    nginx: worker process
   32 nginx    nginx: worker process
   33 nginx    nginx: worker process
   34 nginx    nginx: worker process
   35 nginx    nginx: worker process
   36 nginx    nginx: worker process
   37 nginx    nginx: worker process
   38 nginx    nginx: worker process
   39 nginx    nginx: worker process
   40 nginx    nginx: worker process
   41 nginx    nginx: worker process
   42 nginx    nginx: worker process
   43 nginx    nginx: worker process
   56 root     ps -o pid,user,args
```

Nginx starts one worker per CPU the engine has, so the list is longer on bigger machines. `exec` sees the
container's environment variables, not your computer's:

<!-- test: contains=SHOP_MODE=demo; output -->
```bash
docker exec web env | grep -E '^(SHOP_MODE|NGINX_VERSION|HOSTNAME)='
```

```text
HOSTNAME=2075eb085055
SHOP_MODE=demo
NGINX_VERSION=1.30.5
```

Test the server from inside the container (the container's own `localhost`):

<!-- test: contains=Welcome to nginx!; retry=10; output -->
```bash
docker exec web wget -qO- http://localhost | grep '<title>'
```

```text
<title>Welcome to nginx!</title>
```

For an interactive shell, add `-it` (`-i` keeps input open, `-t` allocates a terminal). Type commands, then `exit`:

<!-- test: skip -->
```bash
docker exec -it web sh
```

On Windows Git Bash, if the shell does not start, use `winpty docker exec -it web sh`.

## Command breakdown

| Command / option | Meaning |
|---|---|
| `docker exec NAME CMD` | run CMD in the running container NAME |
| `-it` | interactive with a terminal: for shells |
| `-u USER` | run as another user (`-u root`, `-u nginx`) |
| `-w DIR` | working directory for the command |
| `-e KEY=VALUE` | an extra environment variable for this command only |
| `sh -c '…'` | needed for pipes, `>`, `&&` inside the container |

## Hands-on lab

**Instructions.** With one `docker exec`, replace the default page of `web` with `<h1>Changed with exec</h1>`, then
fetch it from your computer.

**Expected result.** `Changed with exec` from <http://localhost:8080>.

**Verification.**

<!-- test: contains=Changed with exec; retry=5 -->
```bash
docker exec web sh -c 'echo "<h1>Changed with exec</h1>" > /usr/share/nginx/html/index.html'
curl -s http://localhost:8080
```

Without `sh -c`, the `>` would be interpreted by **your** shell and write a file on your computer.

## Break it

Open a Bash shell, as you would on a server:

<!-- test: fail; contains=executable file not found; output -->
```bash
docker exec web bash 2>&1
```

```text
OCI runtime exec failed: exec failed: unable to start container process: exec: "bash": executable file not found in $PATH
```

## Troubleshoot it

`exec: "bash": executable file not found in $PATH`: the container started, but the program does not exist **in the
image**. Small images (Alpine, distroless) do not include Bash. Check which shells the image has:

<!-- test: contains=/bin/sh; output -->
```bash
docker exec web cat /etc/shells
```

```text
# valid login shells
/bin/sh
/bin/ash
```

Other `exec` errors you will meet:

| Error | Cause |
|---|---|
| `container … is not running` | `exec` needs a running container: read its logs instead (lesson 014) |
| `No such container` | wrong name: check `docker ps` |
| `executable file not found` | the program is not in the image (no shell at all in distroless images: lesson 087) |

## Fix it

Use the shell the image has:

<!-- test: contains=inside the container -->
```bash
docker exec web sh -c 'echo "inside the container, as $(whoami), in $(pwd)"'
```

## Practice challenge

Check the Nginx configuration of `web` for syntax errors and find out which user the **worker** processes run as,
both from outside the container with `docker exec`.

<details>
<summary>Solution</summary>

<!-- test: contains=syntax is ok; contains=nginx; output -->
```bash
docker exec web nginx -t 2>&1
docker exec web ps -o user,args | grep 'worker process' | head -1
```

```text
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
nginx    nginx: worker process
```

`nginx -t` validates the configuration (run it before `nginx -s reload` after a change). The master process runs as
root to open port 80; the workers that handle requests run as the unprivileged user `nginx`.

</details>

## Real-world example

A service cannot reach its database. Instead of guessing, the engineer runs `docker exec api env | grep DB_` to see the
configuration the application actually received, and `docker exec api wget -qO- http://db:5432` or `nc -zv db 5432` to
test the connection from the container's own network. The fix then goes into the image or the deployment
configuration, never stays as a manual change inside the container.

## Recap

- `docker exec` runs an extra process in a running container: same files, network and environment.
- `-it` for interactive shells; `sh -c '…'` for pipes and redirections inside the container.
- `executable file not found`: the program is not in the image; small images often have only `sh`.
- Manual changes made with `exec` are lost when the container is replaced: use it to inspect, not to fix.

## Cleanup

<!-- test -->
```bash
docker rm -f web > /dev/null
```

Next: [Lesson 016 · Inspecting containers](../016-inspecting-containers/README.md)
