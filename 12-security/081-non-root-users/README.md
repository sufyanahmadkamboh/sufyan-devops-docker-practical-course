# Lesson 081 · Running as a non-root user

> Level 13 · Container security · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

Unless the image says otherwise, the process in a container runs as **root** (user ID 0). It is the same user ID 0 that
the host kernel knows: if the process breaks out of the container, through a kernel bug or a careless bind mount, it is
root on the host. The `USER` instruction makes the application run as an ordinary user. The usual problem that follows
is file permissions, and this lesson fixes it properly.

## Visual

```text
  Default: root in the container                     With USER app

  container  python app.py   uid 0 (root)            container  python app.py   uid 100 (app)
     │ escape / bind mount                              │ escape / bind mount
     ▼                                                  ▼
  host       uid 0 = root: can change anything       host       uid 100: an unprivileged user

  Files in the image:  /app/app.py   root:root  read-only for app   (the code cannot be changed)
                       /app/data/    app:app    writable for app    (only what the app must write)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-081 12-security/081-non-root-users/examples/before 12-security/081-non-root-users/examples/broken 12-security/081-non-root-users/examples/fixed
cd ~/docker-practice/lesson-081
ls
```

Three versions of the same small web app (`app.py` records every visit in `data/visits.log`): `before/` runs as root,
`broken/` and `fixed/` try to run as a normal user.

## Demonstration

Which user do containers run as by default?

<!-- test: contains=uid=0(root); output -->
```bash
docker run --rm alpine:3.23 id
```

```text
uid=0(root) gid=0(root) groups=0(root),0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
```

Build the `before` version, start it and ask it:

<!-- test: contains=cafe-web:root -->
```bash
docker build -q -t cafe-web:root before > /dev/null
docker run -d --name web-root -p 8080:8080 cafe-web:root > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

<!-- test: retry=10; contains=uid 0; output -->
```bash
curl -s http://localhost:8080/
```

```text
hello from uid 0
```

`docker top` shows the process as the host sees it, with its user:

<!-- test: contains=root; output -->
```bash
docker top web-root -o user,pid,args
```

```text
USER                PID                 COMMAND
root                2616415             python app.py
```

The web server runs as root, though it only needs to answer HTTP requests on a high port.

## Command breakdown

| Instruction / command | What it does |
|---|---|
| `RUN addgroup -S app && adduser -S -G app -H app` | create a system group and user `app` (Alpine; Debian: `groupadd -r` / `useradd -r`) |
| `USER app` | every later `RUN`, and the container's command, run as `app` |
| `RUN mkdir data && chown app:app data` | give the user only the folder it must write to |
| `COPY --chown=app:app SRC DEST` | copy files owned by a user (only when the app must change them) |
| `docker run --user 1000:1000` | override the user at start time |
| `docker top NAME -o user,pid,args` | the container's processes, with their users, as the host sees them |

## Hands-on lab

**Instructions.** Run the `alpine:3.23` image as user ID 65534 (`nobody`) with `--user 65534:65534` and show its
identity, then try to write to `/root`.

**Expected result.** `uid=65534(nobody)` and `Permission denied` for `/root`.

**Verification.**

<!-- test: contains=uid=65534; contains=Permission denied -->
```bash
docker run --rm --user 65534:65534 alpine:3.23 sh -c 'id; touch /root/test 2>&1 || true'
```

## Break it

The `broken` version adds a user and `USER app`, and nothing else. Build and start it:

<!-- test: contains=cafe-web:broken -->
```bash
docker build -q -t cafe-web:broken broken > /dev/null
docker run -d --name web-broken -p 8081:8080 cafe-web:broken > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

<!-- test: retry=5; contains=Exited (1) -->
```bash
docker ps -a --filter name=web-broken --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

The container exited with status 1. Its logs say why:

<!-- test: contains=PermissionError; output -->
```bash
docker logs web-broken 2>&1 | tail -1
```

```text
PermissionError: [Errno 13] Permission denied: 'data'
```

`Permission denied: 'data'`: the app creates `data/` in `/app`, and `/app` belongs to root. Check who owns it and who
the process is (`--entrypoint` replaces the command, so the container lives long enough to look):

<!-- test: contains=root; contains=uid=; output -->
```bash
docker run --rm --entrypoint sh cafe-web:broken -c 'id; ls -ld /app'
```

```text
uid=100(app) gid=101(app) groups=101(app),101(app)
drwxr-xr-x    1 root     root          4096 Oct  5 16:56 /app
```

The root cause is not `USER`: it is that the image never gave the new user anywhere to write.

## Fix it

Give the user **only** the folder it writes to; the code stays owned by root, so even this user cannot modify it
(see `fixed/Dockerfile`):

<!-- test: contains=chown app:app data; output -->
```bash
grep -n "USER\|chown" fixed/Dockerfile
```

```text
6:RUN mkdir data && chown app:app data
7:USER app
```

<!-- test: contains=cafe-web:fixed -->
```bash
docker rm -f web-broken > /dev/null
docker build -q -t cafe-web:fixed fixed > /dev/null
docker run -d --name web-fixed -p 8081:8080 cafe-web:fixed > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

<!-- test: retry=10; contains=uid 100; output -->
```bash
curl -s http://localhost:8081/
docker exec web-fixed ls -l /app
```

```text
hello from uid 100
total 8
-rwxr-xr-x    1 root     root           696 Oct  5 16:56 app.py
drwxr-xr-x    1 app      app           4096 Oct  5 16:56 data
```

## Practice challenge

Prove that the application in `cafe-web:fixed` cannot modify its own code: as the container's user, try to append a
line to `/app/app.py`. Then show the same command succeeds in `cafe-web:root`.

<details>
<summary>Solution</summary>

<!-- test: contains=Permission denied; contains=root can; output -->
```bash
docker exec web-fixed sh -c 'echo "# changed" >> /app/app.py' 2>&1 || true
docker exec web-root sh -c 'echo "# changed" >> /app/app.py && echo "root can change the code"'
```

```text
sh: can't create /app/app.py: Permission denied
root can change the code
```

In the root container, anyone who gets code execution can rewrite the application. In the fixed one, the code is
read-only for the process; only `data/` is writable.

</details>

## Real-world example

Kubernetes clusters with the `restricted` Pod Security Standard refuse to start containers that run as root
(`runAsNonRoot: true`), so images that rely on root fail at deployment. Teams therefore set `USER` with a fixed numeric
ID in every Dockerfile (`USER 10001`): a numeric ID lets the platform verify "not root" without looking inside the
image.

## Recap

- Containers run as root (uid 0) by default, the same uid 0 as on the host kernel.
- `USER` makes the application run as an unprivileged user.
- "Permission denied" after adding `USER` means the user has nowhere to write: `chown` only the data folder.
- Keep the code owned by root, so a compromised application cannot rewrite itself.

## Cleanup

<!-- test -->
```bash
docker rm -f web-root web-broken web-fixed > /dev/null 2>&1 || true
docker image rm -f cafe-web:root cafe-web:broken cafe-web:fixed > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-081
```

Next: [Lesson 082 · Image security](../082-image-security/README.md)
