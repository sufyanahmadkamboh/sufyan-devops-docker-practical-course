# Lesson 029 · CMD and ENTRYPOINT together

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Used together, `ENTRYPOINT` is the fixed program and `CMD` its **default arguments**. `docker run IMAGE` runs
entrypoint + `CMD`; `docker run IMAGE args` runs entrypoint + your args. This is the most common pattern for tool
images and for service images with an entrypoint script. It only works when both are in exec form.

## Visual

```text
  ENTRYPOINT ["price"]
  CMD ["espresso"]

  docker run IMAGE                    ──▶ price espresso           ENTRYPOINT + CMD
  docker run IMAGE cappuccino         ──▶ price cappuccino         ENTRYPOINT + run args (CMD replaced)
  docker run --entrypoint wc IMAGE -l /app/menu.csv ──▶ wc -l /app/menu.csv

                     │ no ENTRYPOINT            │ ENTRYPOINT ["e"]        │ ENTRYPOINT e (shell form)
  ───────────────────┼──────────────────────────┼─────────────────────────┼──────────────────────────
  no CMD             │ (base image's CMD)       │ e                       │ /bin/sh -c e
  CMD ["c", "x"]     │ c x                      │ e c x                   │ /bin/sh -c e   (CMD lost)
  run args a b       │ a b                      │ e a b                   │ /bin/sh -c e   (args lost)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-029 04-dockerfiles/028-entrypoint/examples
cd ~/docker-practice/lesson-029
ls
```

The `price` tool from lesson 028.

## Demonstration

Give the tool a default argument:

<!-- test: contains=2.50 EUR; contains=3.20 EUR; output -->
```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
COPY menu.csv /app/
COPY --chmod=0755 price.sh /usr/local/bin/price
ENTRYPOINT ["price"]
CMD ["espresso"]
EOF
docker build -q -t price:2.0 . > /dev/null
echo "default:    $(docker run --rm price:2.0)"
echo "cappuccino: $(docker run --rm price:2.0 cappuccino)"
```

```text
default:    2.50 EUR
cappuccino: 3.20 EUR
```

The classic example from the standard tools, `ping` with a fixed count and a default host:

<!-- test: contains=2 packets transmitted; output=tail:2 -->
```bash
printf 'FROM alpine:3.23\nENTRYPOINT ["ping", "-c", "2"]\nCMD ["localhost"]\n' > Dockerfile.ping
docker build -q -f Dockerfile.ping -t pinger . > /dev/null
docker run --rm pinger
```

```text
...
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.103/0.174/0.246 ms
```

`docker run --rm pinger 127.0.0.1` would ping another host, always exactly twice.

## Command breakdown

| Combination | Result |
|---|---|
| `ENTRYPOINT ["e"]` + `CMD ["c"]` | `e c`; run arguments replace `c` |
| `ENTRYPOINT ["e"]`, no `CMD` | `e`; run arguments are appended |
| `ENTRYPOINT e` (shell form) | `/bin/sh -c e`: `CMD` and run arguments are ignored |
| `docker run --entrypoint X IMAGE` | replaces the entrypoint **and** clears the image's `CMD` |

## Hands-on lab

**Instructions.** Run `pinger` against `127.0.0.1` instead of `localhost`, and show the stored entrypoint and command.

**Expected result.** Two pings to 127.0.0.1; `["ping","-c","2"]` and `["localhost"]`.

**Verification.**

<!-- test: contains=PING 127.0.0.1; contains=["localhost"] -->
```bash
docker run --rm pinger 127.0.0.1
docker image inspect --format '{{json .Config.Entrypoint}} {{json .Config.Cmd}}' pinger
```

## Break it

Someone "simplifies" the Dockerfile to the shell form of `ENTRYPOINT`:

<!-- test: fail; contains=usage: price ITEM; output -->
```bash
printf 'FROM alpine:3.23\nCOPY menu.csv /app/\nCOPY --chmod=0755 price.sh /usr/local/bin/price\nENTRYPOINT price\nCMD ["espresso"]\n' > Dockerfile.shell
docker build -q -f Dockerfile.shell -t price:shell . > /dev/null 2>&1
docker run --rm price:shell cappuccino
```

```text
/usr/local/bin/price: line 4: 1: usage: price ITEM
```

## Troubleshoot it

`usage: price ITEM`: the script ran but received **no** argument, neither the `CMD` nor `cappuccino`. Look at what the
container executed:

<!-- test: contains=/bin/sh; contains=JSONArgsRecommended; output -->
```bash
docker run --name price-shell price:shell cappuccino > /dev/null 2>&1 || true
docker container inspect --format 'path={{.Path}} args={{json .Args}}' price-shell
docker rm price-shell > /dev/null
docker build --check -f Dockerfile.shell . 2>&1 | grep -o "WARNING: [A-Za-z]*"
```

```text
path=/bin/sh args=["-c","price","cappuccino"]
WARNING: JSONArgsRecommended
```

The shell form wraps the entrypoint in `/bin/sh -c price`. The extra word `cappuccino` is given to the shell (as its
`$0`), not to `price`, so it is lost. `docker build --check` warns about this combination (`JSONArgsRecommended`).

## Fix it

<!-- test: contains=3.20 EUR -->
```bash
sed -i.bak 's/^ENTRYPOINT price$/ENTRYPOINT ["price"]/' Dockerfile.shell && rm Dockerfile.shell.bak
docker build -q -f Dockerfile.shell -t price:shell . > /dev/null
docker run --rm price:shell cappuccino
```

## Practice challenge

Write the entrypoint-script pattern used by official images: a `docker-entrypoint.sh` that prints
`preparing the cafe…` and then runs whatever command it receives with `exec "$@"`, with `CMD ["price", "espresso"]` as
the default. Verify that the default works and that `docker run IMAGE price "flat white"` works too.

<details>
<summary>Solution</summary>

<!-- test: contains=preparing the cafe; contains=2.50 EUR; contains=3.40 EUR; output -->
```bash
cd ~/docker-practice/lesson-029
printf '#!/bin/sh\nset -e\necho "preparing the cafe..."\nexec "$@"\n' > docker-entrypoint.sh
cat > Dockerfile.script <<'EOF'
FROM alpine:3.23
COPY menu.csv /app/
COPY --chmod=0755 price.sh /usr/local/bin/price
COPY --chmod=0755 docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["price", "espresso"]
EOF
docker build -q -f Dockerfile.script -t price:script . > /dev/null
docker run --rm price:script
docker run --rm price:script price "flat white"
```

```text
preparing the cafe...
2.50 EUR
preparing the cafe...
3.40 EUR
```

The script does its preparation, then `exec "$@"` *replaces* the shell with the command (the `CMD`, or your run
arguments), so the real program becomes the container's main process and receives signals from `docker stop`.

</details>

## Real-world example

The official `postgres` image uses exactly this: `ENTRYPOINT ["docker-entrypoint.sh"]` and `CMD ["postgres"]`. The
script initialises the database on first start (creating users from environment variables, lesson 058), then
`exec`s `postgres`. Because `CMD` is only an argument list, `docker run postgres:18-alpine postgres -c log_statement=all`
passes extra server options through the same script.

## Recap

- With both, `ENTRYPOINT` is the program and `CMD` its default arguments.
- Run arguments replace `CMD`, never `ENTRYPOINT`; `--entrypoint` replaces the entrypoint and clears `CMD`.
- Both must be in exec form: the shell form of `ENTRYPOINT` drops every argument.
- Entrypoint scripts prepare the container and end with `exec "$@"`.

## Cleanup

<!-- test -->
```bash
docker image rm -f price:2.0 price:shell price:script pinger > /dev/null
rm -rf ~/docker-practice/lesson-029
```

Next: [Lesson 030 · ENV](../030-env/README.md)
