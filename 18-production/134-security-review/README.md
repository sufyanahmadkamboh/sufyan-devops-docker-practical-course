# Lesson 134 · Security review

> Level 19 · Production · ⏱ 40 minutes · run every command from the course folder

## What are we learning?

Before an image and its deployment go to production, someone reviews them against a checklist, and proves every
finding with a command instead of guessing from the file. In this lesson you review a real Dockerfile and Compose file
that "work", find nine problems, check the hardened version, and see a classic side effect of hardening: a
read-only container that can no longer start.

## Visual

```text
 Review checklist                                     how to prove it
 ─────────────────────────────────────────────────    ──────────────────────────────────────────────
 IMAGE   1 base image pinned, official, minimal       FROM line; docker image ls
         2 runs as a non-root user                    docker image inspect --format '{{.Config.User}}'
         3 no secrets in ENV / ARG / layers           docker image inspect (Env), docker history --no-trunc
         4 no tools the app does not need             docker run --rm IMG sh -c 'command -v curl bash'
         5 only the needed files (.dockerignore)      docker run --rm IMG ls
         6 exec-form CMD, HEALTHCHECK                 docker image inspect --format '{{.Config.Cmd}} {{.Config.Healthcheck}}'
 RUN     7 not privileged, no Docker socket           docker compose config | grep
         8 only the needed ports published            docker compose config | grep published
         9 secrets as files, resource limits,         docker compose config
           read-only file system, dropped capabilities
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-134 examples/node-api 18-production/134-security-review/examples/before 18-production/134-security-review/examples/broken 18-production/134-security-review/examples/after
cd ~/docker-practice/lesson-134
cp node-api/* before/ && cp node-api/* after/
mkdir -p after/secrets && printf 'example-password-change-me' > after/secrets/db_password.txt
docker build -q -t review-api:before before/ > /dev/null
ls
```

`before/` is the version under review, `after/` the hardened one, `broken/` a first hardening attempt.

## Demonstration

Review `before/`, one checklist item at a time. **Items 1 and 5: base image and files.**

<!-- test: contains=FROM node:24-alpine; output -->
```bash
cd ~/docker-practice/lesson-134
grep FROM before/Dockerfile
docker run --rm review-api:before ls / | tr '\n' ' ' && echo
```

```text
FROM node:24-alpine
Dockerfile bin compose.yaml dev etc home lib media mnt opt package-lock.json package.json proc root run sbin server.js srv sys tmp usr var 
```

The base image is official and pinned to a version (good), but `COPY . .` without `WORKDIR` dropped the application,
including its `compose.yaml` and `Dockerfile`, into the root of the file system, and there is no `.dockerignore`.

**Item 2: the user.**

<!-- test: contains=user=root; output -->
```bash
echo "user=$(docker image inspect review-api:before --format '{{.Config.User}}')" | sed 's/user=$/user=root (none set)/'
```

```text
user=root (none set)
```

**Item 3: secrets.** Both the `ENV` value and the `ARG` default end up readable by anyone who can pull the image:

<!-- test: contains=DB_PASSWORD=example; contains=NPM_TOKEN; output -->
```bash
docker image inspect review-api:before --format '{{range .Config.Env}}{{println .}}{{end}}' | grep PASSWORD
docker history --no-trunc --format '{{.CreatedBy}}' review-api:before | grep -o 'NPM_TOKEN=[^ ]*' | head -1
```

```text
DB_PASSWORD=example-password-change-me
NPM_TOKEN=example-npm-token-change-me
```

**Items 4 and 6: extra tools, the command and the healthcheck.**

<!-- test: contains=/usr/bin/curl; contains=/bin/bash; contains=<nil>; output -->
```bash
docker run --rm review-api:before sh -c 'command -v curl; command -v bash'
docker image inspect review-api:before --format 'cmd={{json .Config.Cmd}} healthcheck={{.Config.Healthcheck}}'
```

```text
/usr/bin/curl
/bin/bash
cmd=["/bin/sh","-c","npm start"] healthcheck=<nil>
```

`curl` and `bash` help an attacker more than the application; the shell-form `CMD` hands the start to a shell and
npm, so whether `SIGTERM` reaches Node.js depends on both of them (lesson 130); there is no healthcheck.

**Items 7–9: the deployment.**

<!-- test: contains=privileged: true; contains=docker.sock; output -->
```bash
docker compose -f before/compose.yaml config | grep -E 'privileged|docker.sock|published|PASSWORD'
```

```text
        published: "3000"
    privileged: true
        source: /var/run/docker.sock
        target: /var/run/docker.sock
      POSTGRES_PASSWORD: example-password-change-me
        published: "5432"
```

The findings:

| # | Finding | Risk | Fix in `after/` |
|---|---|---|---|
| 1 | tag pin only | the tag can move to new content | tag pin, plus digest pin in production (challenge) |
| 2 | runs as root | a container escape starts as root | `USER node` |
| 3 | password in `ENV`, token in `ARG` | anyone with the image reads them | secret files at run time; BuildKit secrets for builds (lesson 083) |
| 4 | `curl`, `bash` installed | tools for an attacker | not installed |
| 5 | `COPY . .` into `/`, no `.dockerignore` | build files and secrets copied into the image | `WORKDIR`, explicit `COPY`, `.dockerignore` |
| 6 | shell-form `CMD`, no `HEALTHCHECK` | slow, unclean stops; "running" but broken | exec form, `HEALTHCHECK` |
| 7 | `privileged: true` + Docker socket | full control of the host | removed |
| 8 | database port published | the database is reachable from outside | no `ports:` on `db` |
| 9 | plain password, no limits, writable file system | leaks, a runaway container takes the host down | `secrets:`, `deploy.resources.limits`, `read_only`, `cap_drop` |

## Command breakdown

| Command | What it proves |
|---|---|
| `docker image inspect --format '{{.Config.User}}'` | empty = root |
| `docker image inspect --format '{{range .Config.Env}}…'` | every environment variable baked into the image |
| `docker history --no-trunc --format '{{.CreatedBy}}'` | the full instruction of every layer, including `ARG` values used in `RUN` |
| `docker run --rm IMG sh -c 'command -v …'` | which tools exist in the image |
| `docker compose -f FILE config` | the final, resolved deployment that Compose would run |

## Hands-on lab

**Instructions.** Run the same checks against the hardened image `review-api:after`: build it, then check the user,
the environment, the tools, the command and the healthcheck.

**Expected result.** User `node`, no password in the environment, neither `curl` nor `bash`, the exec-form command and
a healthcheck.

**Verification.**

<!-- test: contains=user=node; contains=tools=none; contains=["node","server.js"] -->
```bash
cd ~/docker-practice/lesson-134
docker build -q -t review-api:after after/ > /dev/null
echo "user=$(docker image inspect review-api:after --format '{{.Config.User}}')"
docker image inspect review-api:after --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -c PASSWORD || true
echo "tools=$(docker run --rm review-api:after sh -c 'command -v curl || command -v bash' || echo none)"
docker image inspect review-api:after --format 'cmd={{json .Config.Cmd}} healthcheck={{json .Config.Healthcheck.Test}}'
```

## Break it

The first hardening attempt (`broken/compose.yaml`) makes the proxy's file system read-only. Start it:

<!-- test: contains=web -->
```bash
cd ~/docker-practice/lesson-134
cp broken/compose.yaml after/compose.broken.yaml
docker compose -p review -f after/compose.broken.yaml up -d --build --wait 2>&1 | tail -3 || true
docker compose -p review -f after/compose.broken.yaml ps -a --format '{{.Service}}: {{.State}}'
```

The API and the database are fine; `web` has exited.

## Troubleshoot it

<!-- test: contains=Read-only file system; output=tail:2 -->
```bash
docker compose -p review -f after/compose.broken.yaml logs web 2>&1 | grep -i "read-only" | tail -2
```

```text
web-1  | 2026/10/05 12:17:47 [emerg] 1#1: mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
web-1  | nginx: [emerg] mkdir() "/var/cache/nginx/client_temp" failed (30: Read-only file system)
```

Nginx creates temporary directories under `/var/cache/nginx` (for proxied responses) and writes its PID file under
`/run` at startup. With `read_only: true`, every write fails, so Nginx exits. Hardening is right; it just has to
leave writable space where the application really needs it, and nowhere else.

## Fix it

`after/compose.yaml` adds a `tmpfs` (an in-memory, temporary directory) for exactly those two paths:

<!-- test: retry=10; contains=Hello from Node.js -->
```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.broken.yaml down -v > /dev/null 2>&1
grep -A3 "tmpfs" after/compose.yaml
docker compose -p review -f after/compose.yaml up -d --wait > /dev/null 2>&1
docker compose -p review -f after/compose.yaml ps --format '{{.Service}}: {{.State}} {{.Health}}'
curl -s http://localhost:8080/ && echo
```

The file system stays read-only everywhere else:

<!-- test: contains=Read-only file system -->
```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.yaml exec web sh -c 'touch /etc/nginx/hacked' 2>&1 || true
```

## Practice challenge

Finding 1 says production should pin the base image by **digest**, which never moves. Find the digest of your
`node:24-alpine` image and print the `FROM` line that pins it.

<details>
<summary>Solution</summary>

<!-- test: contains=FROM node:24-alpine@sha256:; output -->
```bash
digest=$(docker image inspect node:24-alpine --format '{{range .RepoDigests}}{{println .}}{{end}}' | head -1 | cut -d@ -f2)
echo "FROM node:24-alpine@$digest"
```

```text
FROM node:24-alpine@sha256:ebfe2f90462722a7a4de65e91990e97fe0d401c70e0e762c5b53302f905ec1c1
```

With both, the tag tells people which version it is and the digest guarantees the exact bytes. Tools such as
Dependabot or Renovate update the digest with a reviewed pull request when a new patch release appears.

</details>

## Real-world example

Many teams make this review automatic: a CI step fails the build when an image runs as root, has no healthcheck or
exceeds a size budget (lesson 137), a scanner reports known vulnerabilities, and a policy engine (Kyverno, OPA
Gatekeeper) refuses privileged Pods and Docker socket mounts in the cluster. People then review what tools cannot
judge: is this capability really needed, should this port be public, where does this secret come from.

## Recap

- Review with a checklist and prove every finding with a command (`inspect`, `history`, `run`, `compose config`).
- Common findings: root user, secrets in ENV/ARG, extra tools, privileged mode, the Docker socket, published database
  ports, no limits.
- Harden with `USER`, secret files, `read_only`, `cap_drop: [ALL]`, `no-new-privileges`, resource limits.
- Hardening can break applications that write files: give them `tmpfs` exactly where they need it.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-134
docker compose -p review -f after/compose.yaml down -v > /dev/null 2>&1
docker image rm -f review-api:before review-api:after > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-134
```

Next: [Lesson 135 · Docker in CI](../../19-ci-cd/135-docker-in-ci/README.md)
