# Lesson 024 · WORKDIR

> Level 5 · Dockerfiles · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

`WORKDIR /app` sets the working directory for every instruction after it (`RUN`, `COPY`, `CMD`, `ENTRYPOINT`) and for
the container that runs the image. It creates the directory if it does not exist. Without it, everything happens in
`/`, and a `cd` in a `RUN` step is forgotten as soon as that step ends: each `RUN` starts a fresh shell.

## Visual

```text
  FROM alpine:3.23                 working directory:  /
  WORKDIR /app                     ─────────────────▶  /app         (created if missing)
  COPY menu.csv .                  copies to           /app/menu.csv
  RUN ls                           runs in             /app
  WORKDIR data                     relative: now       /app/data
  CMD ["cat", "../menu.csv"]       the container starts in /app/data

  RUN cd /app   ✗  only changes the directory of that one RUN step's shell; the next step starts in / again
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-024 04-dockerfiles/024-workdir/examples
cd ~/docker-practice/lesson-024
ls
```

`menu.csv` (the cafe's menu) and two Dockerfiles for a "menu service" that prints it.

## Demonstration

`WORKDIR` creates the directory and every later step uses it:

<!-- test: contains=/app/data; output -->
```bash
cat > Dockerfile.demo <<'EOF'
FROM alpine:3.23
WORKDIR /app
COPY menu.csv .
RUN pwd && ls
WORKDIR data
RUN pwd
EOF
docker build --no-cache --progress=plain -f Dockerfile.demo -t workdir-demo . 2>&1 | grep -E '^#[0-9]+ [0-9.]+ '
docker run --rm workdir-demo pwd
```

```text
#8 0.190 /app
#8 0.191 menu.csv
#10 0.193 /app/data
/app/data
```

The `RUN pwd` steps print `/app` and then `/app/data` (a relative `WORKDIR` builds on the previous one), and the
container starts in the last `WORKDIR`. `--progress=plain` shows the output of each `RUN` step; `--no-cache` makes
Docker run them again instead of reusing a previous result (lesson 039).

## Command breakdown

| Instruction / option | Meaning |
|---|---|
| `WORKDIR /path` | set the working directory; created if missing |
| `WORKDIR relative` | relative to the previous `WORKDIR` |
| `COPY file .` | `.` is the current `WORKDIR` |
| `docker run -w /path` | override the working directory for one container |
| `docker build --progress=plain` | show every step's output in full |

## Hands-on lab

**Instructions.** Build `Dockerfile.fixed` as `menu:1.0`, run it, then run the same image with `-w /` and the command
`ls app` to see where the file is.

**Expected result.** The menu is printed; `ls app` in `/` lists `menu.csv`.

**Verification.**

<!-- test: contains=espresso; contains=menu.csv -->
```bash
cd ~/docker-practice/lesson-024
docker build -q -f Dockerfile.fixed -t menu:1.0 . > /dev/null
docker run --rm menu:1.0
docker run --rm -w / menu:1.0 ls app
```

## Break it

A teammate wrote the menu service without `WORKDIR`, with a `cd` instead:

<!-- test: fail; contains=can't open; output -->
```bash
cat Dockerfile.broken
docker build -q -f Dockerfile.broken -t menu:broken . > /dev/null
docker run --rm menu:broken
```

```text
# The menu service: prints the menu
FROM alpine:3.23
COPY menu.csv /app/
RUN cd /app
CMD ["cat", "menu.csv"]
cat: can't open 'menu.csv': No such file or directory
```

The build succeeded, the container fails.

## Troubleshoot it

`can't open 'menu.csv'`: the file was copied, so the question is where the container is looking for it. Check the
image's working directory and where the file really is:

<!-- test: contains=workdir: [/]; contains=/app/menu.csv; output -->
```bash
echo "workdir: [$(docker image inspect --format '{{.Config.WorkingDir}}' menu:broken)]"
docker run --rm menu:broken sh -c 'pwd; ls /app/menu.csv'
```

```text
workdir: [/]
/
/app/menu.csv
```

The image's working directory is `/` (the default when no `WORKDIR` is set), but the file is in `/app`. The
`RUN cd /app` step changed the directory only for its own shell, which ended with the step; it left nothing in the
image.

## Fix it

Replace the `cd` with `WORKDIR`, which is recorded in the image:

<!-- test: contains=espresso; output -->
```bash
diff Dockerfile.broken Dockerfile.fixed || true
docker build -q -f Dockerfile.fixed -t menu:fixed . > /dev/null
docker run --rm menu:fixed
```

```text
3,4c3,4
< COPY menu.csv /app/
< RUN cd /app
---
> WORKDIR /app
> COPY menu.csv .
item,price
espresso,2.50
cappuccino,3.20
flat white,3.40
```

When you really need another directory for one step, `cd` inside that `RUN`: `RUN cd /tmp && tar -xzf tools.tgz`.

## Practice challenge

Write a Dockerfile that copies `menu.csv` into `/srv/cafe/menu/`, and whose container prints the number of lines of
the file with `wc -l menu.csv` (a relative path), using `WORKDIR` twice: `/srv/cafe`, then `menu`.

<details>
<summary>Solution</summary>

<!-- test: contains=4 menu.csv; output -->
```bash
cd ~/docker-practice/lesson-024
printf 'FROM alpine:3.23\nWORKDIR /srv/cafe\nWORKDIR menu\nCOPY menu.csv .\nCMD ["wc", "-l", "menu.csv"]\n' > Dockerfile.challenge
docker build -q -f Dockerfile.challenge -t menu:challenge . > /dev/null
docker run --rm menu:challenge
```

```text
4 menu.csv
```

The second, relative `WORKDIR` makes the working directory `/srv/cafe/menu`; `COPY … .` and the command both use it.

</details>

## Real-world example

Official language images set a `WORKDIR` convention that application Dockerfiles follow: `WORKDIR /app` (or
`/usr/src/app`), then `COPY` and `CMD` with relative paths. Anyone who opens a shell in a container of the team's images
(`docker exec -it … sh`, lesson 015) lands in the application's folder, and tools that mount source code for
development (Compose, lesson 066) mount it at the same path.

## Recap

- `WORKDIR` sets the directory for later instructions and for the container, creating it if needed.
- A relative `WORKDIR` builds on the previous one.
- `RUN cd …` only affects that one step; use `WORKDIR` instead.
- Check an image's working directory with `docker image inspect --format '{{.Config.WorkingDir}}'`.

## Cleanup

<!-- test -->
```bash
docker image rm -f workdir-demo menu:1.0 menu:broken menu:fixed menu:challenge > /dev/null
rm -rf ~/docker-practice/lesson-024
```

Next: [Lesson 025 · COPY and ADD](../025-copy-and-add/README.md)
