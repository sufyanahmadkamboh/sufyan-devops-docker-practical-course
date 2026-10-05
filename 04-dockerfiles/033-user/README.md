# Lesson 033 · USER

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Unless the image says otherwise, a container's process runs as **root** (user ID 0). `USER appuser` switches the
following `RUN` steps and the container to a normal user. If the application is compromised, the attacker then has the
rights of a normal user inside the container, not root's (lesson 081 goes deeper). The price: that user can only write
where you allow it to, so files and folders need the right owner.

## Visual

```text
  FROM alpine:3.23
  RUN adduser -S -u 10001 appuser        create the user (as root)
  WORKDIR /app
  COPY take-order.sh .                   owned by root: appuser can read and run it, not change it
  RUN mkdir data && chown appuser data   the one folder appuser may write to
  USER appuser                           ── everything below, and the container, runs as uid 10001
  ENTRYPOINT ["./take-order.sh"]

  /app            root:root    r-x for appuser      code: read-only for the application
  /app/data       appuser      rwx for appuser      data: writable
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-033 04-dockerfiles/033-user/examples
cd ~/docker-practice/lesson-033
cat take-order.sh
```

The order service appends each order to an order log and prints the log.

## Demonstration

Most images run as root by default:

<!-- test: contains=uid=0(root); output -->
```bash
docker run --rm alpine:3.23 id
```

```text
uid=0(root) gid=0(root) groups=0(root),0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
```

Some official images already contain a non-root user for you; `node` images have `node` (uid 1000):

<!-- test: contains=uid=1000(node); output -->
```bash
docker run --rm --user node node:24-alpine id
```

```text
uid=1000(node) gid=1000(node) groups=1000(node),1000(node)
```

Create your own user and switch to it:

<!-- test: contains=uid=10001(appuser); output -->
```bash
printf 'FROM alpine:3.23\nRUN addgroup -S cafe && adduser -S -G cafe -u 10001 appuser\nUSER appuser\nCMD ["id"]\n' > Dockerfile.id
docker build -q -f Dockerfile.id -t user-demo:id . > /dev/null
docker run --rm user-demo:id
docker image inspect --format 'image user: {{.Config.User}}' user-demo:id
```

```text
uid=10001(appuser) gid=101(cafe) groups=101(cafe),101(cafe)
image user: appuser
```

## Command breakdown

| Instruction / option | Meaning |
|---|---|
| `adduser -S -G GROUP -u UID NAME` | Alpine: create a system user (`-S`: no password, no login shell) |
| `useradd --system --uid UID NAME` | Debian/Ubuntu equivalent |
| `USER NAME` or `USER UID[:GID]` | run the following steps and the container as that user |
| `COPY --chown=USER:GROUP` | copy files with an owner (lesson 025) |
| `docker run --user UID` | override the user for one container |
| `docker image inspect --format '{{.Config.User}}'` | the image's user; empty means root |

## Hands-on lab

**Instructions.** Build `Dockerfile.fixed` as `orders:1.0`, take an order for a cappuccino, and check who owns the order
log.

**Expected result.** The log shows the order; the file belongs to `appuser`.

**Verification.**

<!-- test: contains=cappuccino; contains=appuser -->
```bash
cd ~/docker-practice/lesson-033
docker build -q -f Dockerfile.fixed -t orders:1.0 . > /dev/null
docker run --rm orders:1.0 cappuccino
docker run --rm --entrypoint sh orders:1.0 -c './take-order.sh latte > /dev/null; ls -l /app/data'
```

## Break it

The first attempt at a non-root order service only adds `USER`:

<!-- test: fail; contains=Permission denied; output -->
```bash
docker build -q -f Dockerfile.broken -t orders:broken . > /dev/null
docker run --rm orders:broken espresso
```

```text
./take-order.sh: line 4: can't create /app/orders.log: Permission denied
```

## Troubleshoot it

`can't create /app/orders.log: Permission denied`: the script runs, but cannot create its file. Compare the user with
the owner of the folder:

<!-- test: contains=uid=10001(appuser); contains=root; output -->
```bash
docker run --rm --entrypoint sh orders:broken -c 'id; ls -ld /app; ls -l /app'
```

```text
uid=10001(appuser) gid=101(cafe) groups=101(cafe),101(cafe)
drwxr-xr-x    1 root     root          4096 Oct  5 11:59 /app
total 4
-rwxr-xr-x    1 root     root           204 Oct  5 11:59 take-order.sh
```

`WORKDIR` and `COPY` ran as root, so `/app` belongs to root and only root may create files in it. Under root, the
mistake was invisible, because root may write everywhere.

Do not "fix" it by going back to root (`USER root`, `docker run --user 0`): that removes the protection you wanted.

## Fix it

Give the user exactly one writable place, and leave the code owned by root:

<!-- test: contains=espresso; output -->
```bash
diff Dockerfile.broken Dockerfile.fixed || true
docker build -q -f Dockerfile.fixed -t orders:fixed . > /dev/null
docker run --rm orders:fixed espresso
```

```text
5a6,8
> # the code stays owned by root (read-only for appuser); only the data folder is writable
> RUN mkdir /app/data && chown appuser:cafe /app/data
> ENV ORDER_LOG=/app/data/orders.log
16:55:06 espresso
```

The application can no longer modify its own code (an attacker cannot either), and its data can live in a volume
mounted at `/app/data` (lesson 055).

## Practice challenge

Prove that in `orders:fixed` the application cannot change its own script, but can write its data.

<details>
<summary>Solution</summary>

<!-- test: contains=script: Permission denied; contains=data: ok; output -->
```bash
docker run --rm --entrypoint sh orders:fixed -c '
  (echo "# changed" >> /app/take-order.sh) 2>/dev/null && echo "script: changed" || echo "script: Permission denied"
  touch /app/data/test && echo "data: ok"'
```

```text
script: Permission denied
data: ok
```

</details>

## Real-world example

Kubernetes clusters commonly enforce `runAsNonRoot: true` through Pod Security Standards: a container whose image runs
as root is refused. Images therefore end with a **numeric** `USER 10001` (Kubernetes cannot check a user *name*), and
the application writes only to mounted volumes or `/tmp`. Images such as `nginxinc/nginx-unprivileged` and the
`:nonroot` distroless variants exist for exactly this reason.

## Recap

- Containers run as root unless the image or `docker run --user` says otherwise.
- Create a user (`adduser`/`useradd`) and switch with `USER`, preferably by numeric ID.
- Files created before `USER` belong to root: give the user only the folders it must write to.
- Never fix permission errors by switching back to root.

## Cleanup

<!-- test -->
```bash
docker image rm -f user-demo:id orders:1.0 orders:broken orders:fixed > /dev/null
rm -rf ~/docker-practice/lesson-033
```

Next: [Lesson 034 · Dockerfile best practices](../034-dockerfile-best-practices/README.md)
