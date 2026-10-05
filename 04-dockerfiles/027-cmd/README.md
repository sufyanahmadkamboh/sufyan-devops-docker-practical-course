# Lesson 027 · CMD

> Level 5 · Dockerfiles · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

`CMD` sets the **default command** of a container: what runs when you `docker run IMAGE` without a command. It does
nothing at build time. Anything you write after the image name in `docker run` replaces it. A Dockerfile has one
effective `CMD` (the last one), and it should be written in **exec form**, a JSON array with double quotes.

## Visual

```text
  Dockerfile:  CMD ["cat", "/app/menu.csv"]          stored in the image as its default command

  docker run menu                 ──▶ cat /app/menu.csv           (the default)
  docker run menu ls /app         ──▶ ls /app                     (replaced: everything after the image name)
  docker run menu wc -l /app/menu.csv ──▶ wc -l /app/menu.csv

  exec form   CMD ["echo", "hi"]  ──▶ runs echo directly: it is the container's main process (PID 1)
  shell form  CMD echo hi         ──▶ runs /bin/sh -c "echo hi": $VARIABLES are expanded by the shell
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-027 04-dockerfiles/024-workdir/examples
cd ~/docker-practice/lesson-027
rm Dockerfile.*
ls
```

The cafe's `menu.csv` from lesson 024.

## Demonstration

<!-- test: contains=espresso; output -->
```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
WORKDIR /app
COPY menu.csv .
CMD ["cat", "menu.csv"]
EOF
docker build -q -t menu:cmd . > /dev/null
docker run --rm menu:cmd
```

```text
item,price
espresso,2.50
cappuccino,3.20
flat white,3.40
```

A command after the image name replaces `CMD` completely:

<!-- test: contains=4 menu.csv; output -->
```bash
docker run --rm menu:cmd wc -l menu.csv
```

```text
4 menu.csv
```

The default command is stored in the image's configuration:

<!-- test: contains=["cat","menu.csv"]; output -->
```bash
docker image inspect --format '{{json .Config.Cmd}}' menu:cmd
```

```text
["cat","menu.csv"]
```

The two forms differ in whether a shell is involved. Only the shell form expands variables:

<!-- test: contains=shell form: /root; contains=exec form: $HOME; output -->
```bash
printf 'FROM alpine:3.23\nCMD echo "shell form: $HOME"\n' > Dockerfile.shell
printf 'FROM alpine:3.23\nCMD ["echo", "exec form: $HOME"]\n' > Dockerfile.exec
docker build -q -f Dockerfile.shell -t cmd-form:shell . > /dev/null
docker build -q -f Dockerfile.exec -t cmd-form:exec . > /dev/null
docker run --rm cmd-form:shell
docker run --rm cmd-form:exec
```

```text
shell form: /root
exec form: $HOME
```

Prefer the exec form: the program itself is the container's main process and receives `docker stop`'s signal directly.
With the shell form, `/bin/sh` sits in between and may not pass signals on, so the application cannot shut down
cleanly. When you need a shell, say so explicitly: `CMD ["sh", "-c", "echo $HOME"]`.

## Command breakdown

| Form | Meaning |
|---|---|
| `CMD ["prog", "arg"]` | exec form (preferred): JSON array, **double** quotes |
| `CMD prog arg` | shell form: `/bin/sh -c "prog arg"` |
| `CMD ["arg1", "arg2"]` after an `ENTRYPOINT` | default arguments for the entrypoint (lesson 029) |
| `docker run IMAGE COMMAND…` | replace `CMD` for this container |
| `docker image inspect --format '{{json .Config.Cmd}}'` | show an image's default command |

## Hands-on lab

**Instructions.** Run `menu:cmd` three times: with its default command, with `head -2 menu.csv`, and with
`grep cappuccino menu.csv`.

**Expected result.** The whole menu, the first two lines, and the cappuccino line.

**Verification.**

<!-- test: contains=cappuccino,3.20 -->
```bash
docker run --rm menu:cmd
docker run --rm menu:cmd head -2 menu.csv
docker run --rm menu:cmd grep cappuccino menu.csv
```

## Break it

A colleague writes the exec form with single quotes, as in Python:

<!-- test: fail; contains=not found; output -->
```bash
printf "FROM alpine:3.23\nCMD ['echo', 'hello']\n" > Dockerfile.quotes
docker build -q -f Dockerfile.quotes -t cmd-form:quotes . > /dev/null
docker run --rm cmd-form:quotes
```

```text
/bin/sh: [echo,: not found
```

## Troubleshoot it

The build worked, the container fails with exit status 127 ("command not found"), and the "command" it tried is
`[echo,`. Look at what Docker stored:

<!-- test: contains=/bin/sh; output -->
```bash
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:quotes
```

```text
["/bin/sh","-c","['echo', 'hello']"]
```

Single quotes are not valid JSON, so Docker did not recognise an exec-form array and treated the whole line as a
**shell-form** command. The shell then split it into words and tried to run a program called `[echo,`. The build
checker spots this without building:

<!-- test: contains=JSONArgsRecommended -->
```bash
docker build --check -f Dockerfile.quotes . 2>&1 | grep -A1 WARNING
```

## Fix it

Use double quotes, as JSON requires:

<!-- test: contains=hello; output -->
```bash
printf 'FROM alpine:3.23\nCMD ["echo", "hello"]\n' > Dockerfile.quotes
docker build -q -f Dockerfile.quotes -t cmd-form:quotes . > /dev/null
docker run --rm cmd-form:quotes
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:quotes
```

```text
hello
["echo","hello"]
```

## Practice challenge

A Dockerfile has two `CMD` lines: `CMD ["echo", "first"]` and then `CMD ["echo", "second"]`. Predict what the
container prints, then prove it, and show that only one default command is stored.

<details>
<summary>Solution</summary>

<!-- test: contains=second; absent=first; contains=MultipleInstructionsDisallowed; output -->
```bash
cd ~/docker-practice/lesson-027
printf 'FROM alpine:3.23\nCMD ["echo", "first"]\nCMD ["echo", "second"]\n' > Dockerfile.twice
docker build -q -f Dockerfile.twice -t cmd-form:twice . > /dev/null 2>&1
docker run --rm cmd-form:twice
docker image inspect --format '{{json .Config.Cmd}}' cmd-form:twice
docker build --check -f Dockerfile.twice . 2>&1 | grep -o "WARNING: [A-Za-z]*"
```

```text
second
["echo","second"]
WARNING: MultipleInstructionsDisallowed
```

Each `CMD` overwrites the previous one: only the last counts. This also applies to the base image's `CMD`: `alpine`
sets `CMD ["/bin/sh"]`, and your `CMD` replaces it. `docker build --check` reports `MultipleInstructionsDisallowed`
for the duplicate.

</details>

## Real-world example

The official `nginx` image ends with `CMD ["nginx", "-g", "daemon off;"]`, and the `python` images with
`CMD ["python3"]`. An application image based on them sets its own `CMD` (for example
`CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]`), and operators still run one-off tasks with the same image by
replacing it: `docker run --rm cafe-api:1.4 python manage.py migrate`.

## Recap

- `CMD` is the default command of the container; it does nothing at build time.
- Arguments after the image name in `docker run` replace it entirely.
- Only the last `CMD` counts; it also replaces the base image's `CMD`.
- Use the exec form with double quotes; single quotes silently turn it into shell form.

## Cleanup

<!-- test -->
```bash
docker image rm -f menu:cmd cmd-form:shell cmd-form:exec cmd-form:quotes cmd-form:twice > /dev/null
rm -rf ~/docker-practice/lesson-027
```

Next: [Lesson 028 · ENTRYPOINT](../028-entrypoint/README.md)
