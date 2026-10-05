# Lesson 060 · Environment files

> Level 10 · Environment configuration · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Ten `-e` flags make an unreadable command and leak values into your shell history. An **env file** collects them:
one `NAME=value` per line, comments with `#`, passed with `--env-file FILE`. One file per environment
(`dev.env`, `staging.env`) keeps configuration versioned and reviewable. The format is deliberately simple, and that
is the trap: `docker run` does **not** interpret quotes, so `NAME="value"` gives a value that includes the quotes.

## Visual

```text
  app.env                                  docker run --env-file app.env -e LOG_LEVEL=debug IMAGE
 ┌───────────────────────────────┐                     │
 │ # cafe API, development       │                     ▼
 │ GREETING=Welcome to the cafe  │         container environment
 │ APP_VERSION=1.4.0             │           GREETING=Welcome to the cafe
 │ LOG_LEVEL=info                │           APP_VERSION=1.4.0
 └───────────────────────────────┘           LOG_LEVEL=debug        ← -e wins over the file

  rules: NAME=value · no spaces around = · everything after = is the value, quotes included · # comments
  commit:  app.env.example (no secrets)         never commit:  .env files with real passwords
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-060 examples/node-api
cd ~/docker-practice/lesson-060
printf '# cafe API, development\nGREETING=Welcome to the cafe\nAPP_VERSION=1.4.0\nLOG_LEVEL=info\n' > app.env
cat app.env
```

## Demonstration

Pass the whole file:

<!-- test: contains=Welcome to the cafe; output; retry=5 -->
```bash
docker run -d --name api -p 8080:3000 --env-file app.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8080; echo
```

```text
{"message":"Welcome to the cafe","hostname":"bb3d86fa242c","version":"1.4.0"}
```

The comment line was ignored; every other line became a variable:

<!-- test: contains=LOG_LEVEL=info; output -->
```bash
docker inspect api --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -E 'GREETING|APP_VERSION|LOG_LEVEL'
```

```text
GREETING=Welcome to the cafe
APP_VERSION=1.4.0
LOG_LEVEL=info
```

`-e` on the command line overrides a value from the file:

<!-- test: contains=LOG_LEVEL=debug; output -->
```bash
docker run --rm --env-file app.env -e LOG_LEVEL=debug alpine:3.23 sh -c 'echo "LOG_LEVEL=$LOG_LEVEL"'
```

```text
LOG_LEVEL=debug
```

## Command breakdown

| Form | Meaning |
|---|---|
| `--env-file FILE` | read `NAME=value` lines from FILE (repeatable: later files override earlier ones) |
| `# …` | a comment line |
| `NAME` alone on a line | copy NAME from the shell, like `-e NAME` |
| `-e NAME=value` | overrides the same variable from any env file |

## Hands-on lab

**Instructions.** Write a second file `prod.env` that changes only `GREETING` and `LOG_LEVEL`, and start a container
with **both** files (`app.env` first) to see which values win.

**Expected result.** `APP_VERSION=1.4.0` from `app.env`; `GREETING` and `LOG_LEVEL` from `prod.env`.

**Verification.**

<!-- test: contains=APP_VERSION=1.4.0; contains=LOG_LEVEL=warn; contains=GREETING=Welcome -->
```bash
printf 'GREETING=Welcome, production guest\nLOG_LEVEL=warn\n' > prod.env
docker run --rm --env-file app.env --env-file prod.env alpine:3.23 sh -c 'env | grep -E "GREETING|APP_VERSION|LOG_LEVEL" | sort'
```

## Break it

Someone "cleans up" the file in the style of a shell script, with quotes:

<!-- test: contains=\"Welcome to the cafe\"; output; retry=5 -->
```bash
printf 'GREETING="Welcome to the cafe"\nAPP_VERSION=1.4.0\n' > quoted.env
docker run -d --name quoted -p 8081:3000 --env-file quoted.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8081; echo
```

```text
{"message":"\"Welcome to the cafe\"","hostname":"9be44f568f46","version":"1.4.0"}
```

## Troubleshoot it

The greeting now contains the quotes: `"\"Welcome to the cafe\""` in the JSON. Look at the value exactly as the
container received it:

<!-- test: contains=GREETING="Welcome to the cafe"; output -->
```bash
docker exec quoted printenv GREETING | sed 's/^/GREETING=/'
```

```text
GREETING="Welcome to the cafe"
```

`docker run --env-file` takes everything after `=` literally: no quote removal, no `$VARIABLE` expansion, no
escaping. (Docker Compose's `.env` handling does remove quotes, which is why the two get mixed up.)

## Fix it

Write values without quotes; spaces inside a value need no quoting:

<!-- test: contains="message":"Welcome to the cafe"; output; retry=5 -->
```bash
printf 'GREETING=Welcome to the cafe\nAPP_VERSION=1.4.0\n' > quoted.env
docker rm -f quoted > /dev/null
docker run -d --name quoted -p 8081:3000 --env-file quoted.env -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8081; echo
```

```text
{"message":"Welcome to the cafe","hostname":"af0a2afce13c","version":"1.4.0"}
```

## Practice challenge

An env file line can be just a variable name. Use that to pass `RELEASE` from your shell through the file, without
writing its value into the file.

<details>
<summary>Solution</summary>

<!-- test: contains=release 2026.10; output -->
```bash
printf 'RELEASE\n' > release.env
export RELEASE=2026.10
docker run --rm --env-file release.env alpine:3.23 sh -c 'echo "release $RELEASE"'
```

```text
release 2026.10
```

The file lists **which** variables the container gets; the values come from the environment of whoever runs
`docker`, such as a CI job. That keeps values that change per run (or secrets) out of the file.

</details>

## Real-world example

A team keeps `config/dev.env`, `config/staging.env` and `config/prod.env` in Git, without passwords. Changing a
setting is a reviewed pull request, and `git log config/prod.env` shows who changed what and when. Passwords are
injected separately by the deployment system (lesson 061), and `.gitignore` contains `*.local.env` for developers'
private overrides.

## Recap

- `--env-file FILE` passes many variables at once; `#` lines are comments.
- Values are literal: no quotes, no `$` expansion; quotes become part of the value.
- Later files override earlier ones; `-e` overrides any file.
- Keep env files without secrets in Git; never commit real passwords in them.

## Cleanup

<!-- test -->
```bash
docker rm -f api quoted > /dev/null
rm -rf ~/docker-practice/lesson-060
```

Next: [Lesson 061 · Configuration vs secrets](../061-config-vs-secrets/README.md)
