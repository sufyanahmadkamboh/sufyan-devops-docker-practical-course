# Lesson 028 · ENTRYPOINT

> Level 5 · Dockerfiles · ⏱ 15 minutes · run every command from the course folder

## What are we learning?

`ENTRYPOINT` sets the program a container **always** runs. Unlike `CMD`, it is not replaced by the arguments of
`docker run`: they are **appended** to it. That turns an image into a command-line tool (`docker run price espresso`
works like `price espresso`). To run something else, you must say so explicitly with `--entrypoint`.

## Visual

```text
  Dockerfile:  ENTRYPOINT ["price"]

  docker run price espresso          ──▶ price espresso          arguments are appended
  docker run price "flat white"      ──▶ price "flat white"
  docker run price sh                ──▶ price sh                ✗ "sh" is just another argument
  docker run --entrypoint sh price   ──▶ sh                      the entrypoint replaced, for this container only

              CMD                               ENTRYPOINT
  run args    replace it                        are appended to it
  override    docker run IMAGE other-command    docker run --entrypoint other IMAGE
  use for     a default that is often changed   the image's fixed main program
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-028 04-dockerfiles/028-entrypoint/examples
cd ~/docker-practice/lesson-028
cat price.sh Dockerfile
```

`price.sh` looks up an item in the menu. The Dockerfile installs it as `/usr/local/bin/price` and makes it the
entrypoint. (`COPY --chmod=0755` makes the script executable, lesson 025.)

## Demonstration

<!-- test: contains=2.50 EUR; contains=3.40 EUR; output -->
```bash
docker build -q -t price:1.0 . > /dev/null
docker run --rm price:1.0 espresso
docker run --rm price:1.0 "flat white"
```

```text
2.50 EUR
3.40 EUR
```

The image behaves like a program: everything after the image name became the script's argument. The script's exit
status is the container's exit status, so a failure is visible to scripts and CI:

<!-- test: contains=unknown item: tea; contains=exit status 1; output -->
```bash
docker run --rm price:1.0 tea || echo "exit status $?"
```

```text
unknown item: tea
exit status 1
```

## Command breakdown

| Instruction / option | Meaning |
|---|---|
| `ENTRYPOINT ["prog", "arg"]` | exec form (preferred): `docker run` arguments are appended |
| `ENTRYPOINT prog arg` | shell form: runs through `/bin/sh -c`, and **ignores** both `CMD` and run arguments |
| `docker run --entrypoint PROG IMAGE ARGS…` | replace the entrypoint for one container; ARGS go to PROG |
| `docker image inspect --format '{{json .Config.Entrypoint}}'` | show an image's entrypoint |

## Hands-on lab

**Instructions.** Look up the price of a cappuccino, then show the image's entrypoint with `docker image inspect`.

**Expected result.** `3.20 EUR` and `["price"]`.

**Verification.**

<!-- test: contains=3.20 EUR; contains=["price"] -->
```bash
docker run --rm price:1.0 cappuccino
docker image inspect --format '{{json .Config.Entrypoint}}' price:1.0
```

## Break it

You want to look inside the image, so you ask for a shell the usual way:

<!-- test: fail; contains=unknown item: sh; output -->
```bash
docker run --rm price:1.0 sh
```

```text
unknown item: sh
```

## Troubleshoot it

`unknown item: sh`: the message comes from `price.sh`, so the script ran and received `sh` as an item name. With an
`ENTRYPOINT`, the words after the image name are arguments, never a new command. Check what the container really
executed:

<!-- test: contains=price; output -->
```bash
docker run --name price-check price:1.0 sh > /dev/null 2>&1 || true
docker container inspect --format 'path={{.Path}} args={{json .Args}}' price-check
docker rm price-check > /dev/null
```

```text
path=price args=["sh"]
```

## Fix it

Replace the entrypoint for this one container; the arguments after the image name now go to the new program:

<!-- test: contains=/app/menu.csv; contains=/usr/local/bin/price; output -->
```bash
docker run --rm --entrypoint sh price:1.0 -c 'ls /app/menu.csv /usr/local/bin/price'
```

```text
/app/menu.csv
/usr/local/bin/price
```

For an interactive shell, `docker run --rm -it --entrypoint sh price:1.0`.

## Practice challenge

Without changing the image, use `--entrypoint` to count the lines of `/app/menu.csv` with `wc -l`.

<details>
<summary>Solution</summary>

<!-- test: contains=4 /app/menu.csv; output -->
```bash
docker run --rm --entrypoint wc price:1.0 -l /app/menu.csv
```

```text
4 /app/menu.csv
```

`--entrypoint` takes only the program name; its arguments come after the image name.

</details>

## Real-world example

Many tool images are built this way: `docker run --rm -v "$(pwd):/work" -w /work hadolint/hadolint …`,
`docker run --rm aquasec/trivy image cafe-api:1.4`, or a team's own `migrate` image in a deployment pipeline. Official
service images often use an entrypoint *script* (`/docker-entrypoint.sh` in `nginx`, `postgres`, `redis`) that prepares
configuration and then `exec`s the real program, so the program still becomes the main process.

## Recap

- `ENTRYPOINT` is the program a container always runs; `docker run` arguments are appended to it.
- `--entrypoint` replaces it for one container; arguments after the image name go to the new program.
- Use the exec form; the shell form ignores all arguments.
- The entrypoint's exit status is the container's exit status.

## Cleanup

<!-- test -->
```bash
docker image rm -f price:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-028
```

Next: [Lesson 029 · CMD and ENTRYPOINT together](../029-cmd-and-entrypoint/README.md)
