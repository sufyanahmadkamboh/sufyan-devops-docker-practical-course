# Lesson 034 · Dockerfile best practices

> Level 5 · Dockerfiles · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A Dockerfile that "works" can still be slow to rebuild, larger than needed, run as root and stop badly. This lesson
reviews a first version of the cafe API's Dockerfile against the practices of this module, measures the difference,
and uses Docker's built-in checker (`docker build --check`) to catch mistakes before they ship.

## Visual

```text
  Dockerfile.before                         Dockerfile.after
  FROM node:24-alpine                       FROM node:24-alpine                   pinned, small base       (023)
  COPY . /app            ← everything       ENV NODE_ENV=production
  WORKDIR /app                              WORKDIR /app                          WORKDIR before use       (024)
  RUN npm install        ← after the code   COPY package.json package-lock.json ./  dependencies first     (025, 039)
                                            RUN npm ci --omit=dev && npm cache clean --force  one clean step (026)
                                            COPY server.js ./                     then only the code
                                            USER node                             not root                 (033)
  EXPOSE 3000                               EXPOSE 3000                           documented port          (032)
  CMD node server.js     ← shell form       CMD ["node", "server.js"]             exec form                (027)
                                            + Dockerfile.after.dockerignore       a small build context    (037)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-034 examples/node-api
cp 04-dockerfiles/034-dockerfile-best-practices/examples/Dockerfile.* ~/docker-practice/lesson-034/
cd ~/docker-practice/lesson-034
mkdir -p notes && echo "meeting notes, not for the image" > notes/todo.md
ls -A
```

The Node.js API, the two Dockerfiles, a `.dockerignore` file for the second one, and a `notes/` folder that does not
belong in any image.

## Demonstration

Build both versions:

<!-- test: contains=cafe-api:before; contains=cafe-api:after -->
```bash
docker build -q -f Dockerfile.before -t cafe-api:before . > /dev/null
docker build -q -f Dockerfile.after -t cafe-api:after . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.Size}}' cafe-api
```

Both images run the same application. Compare what is inside and who runs it:

<!-- test: contains=before: root; contains=after: node; output -->
```bash
for v in before after; do
  echo "$v: $(docker run --rm cafe-api:$v whoami), files in /app: $(docker run --rm cafe-api:$v ls -A /app | tr '\n' ' ')"
done
```

```text
before: root, files in /app: Dockerfile.after Dockerfile.after.dockerignore Dockerfile.before notes package-lock.json package.json server.js 
after: node, files in /app: package-lock.json package.json server.js 
```

The first image runs as root and contains the Dockerfiles and the private notes; the second contains only what the
application needs. A `.dockerignore` file named after the Dockerfile (`Dockerfile.after.dockerignore`) applies only to
builds with that Dockerfile; the usual name is `.dockerignore` next to `Dockerfile` (lesson 037).

## Command breakdown

| Practice | Why |
|---|---|
| pin the base tag (or digest) | reproducible builds (lessons 021, 023) |
| copy dependency files first, then the code | code changes do not re-install dependencies (lesson 039) |
| `npm ci` / pinned versions | installs exactly the lock file |
| clean caches in the same `RUN` | smaller layers (lesson 017) |
| `.dockerignore` | small context; no secrets or junk in the image (lesson 037) |
| `USER` a non-root user | less damage if the application is compromised (lesson 033) |
| exec form `CMD`/`ENTRYPOINT` | signals reach the application (lesson 027) |
| `docker build --check` | Docker's built-in Dockerfile checks, without building |

## Hands-on lab

**Instructions.** Change one line of `server.js` (the default greeting), then rebuild **both** images with
`--progress=plain` and count how many steps were taken from the cache.

**Expected result.** In the `after` build, the `npm ci` step is `CACHED`; in the `before` build, `npm install` runs
again.

**Verification.**

<!-- test: contains=after: npm ci CACHED; contains=before: npm install ran again -->
```bash
cd ~/docker-practice/lesson-034
sed -i.bak 's/Hello from Node.js/Hello from the cafe/' server.js && rm server.js.bak
docker build --progress=plain -f Dockerfile.after -t cafe-api:after . 2>&1 | grep -A1 'RUN npm ci' | grep -q CACHED && echo "after: npm ci CACHED"
docker build --progress=plain -f Dockerfile.before -t cafe-api:before . 2>&1 | grep -A1 'RUN npm install' | grep -q CACHED || echo "before: npm install ran again"
```

The application has no dependencies, so `npm install` is quick here; with a few hundred packages it takes minutes, on
every code change.

## Break it

Ask Docker's checker about the first version:

<!-- test: fail; contains=JSONArgsRecommended; output=tail:9 -->
```bash
docker build --check -f Dockerfile.before . 2>&1
```

```text
...
WARNING: JSONArgsRecommended - https://docs.docker.com/go/dockerfile/rule/json-args-recommended/
JSON arguments recommended for CMD to prevent unintended behavior related to OS signals
Dockerfile.before:7
--------------------
   5 |     RUN npm install
   6 |     EXPOSE 3000
   7 | >>> CMD node server.js
   8 |     
--------------------
```

## Troubleshoot it

`--check` runs Docker's build checks (rules such as `JSONArgsRecommended`, `SecretsUsedInArgOrEnv`, `FromAsCasing`,
`UndefinedVar`) without building, and exits with status 1 when it finds something, so it can fail a CI job. Each
warning names the rule, links to its documentation, and marks the line. It cannot see everything: running as root and
copying the whole folder are not "errors", so a review against the practices above is still needed. Here it found the
shell-form `CMD`: `node` is started through `/bin/sh -c`. Some shells replace themselves with a single command,
others stay in between and do not pass `docker stop`'s signal on; with the exec form there is no doubt.

<!-- test: contains=/bin/sh; output -->
```bash
docker image inspect --format '{{json .Config.Cmd}}' cafe-api:before
```

```text
["/bin/sh","-c","node server.js"]
```

## Fix it

The improved version passes the checks:

<!-- test: contains=no warnings -->
```bash
docker build --check -f Dockerfile.after . 2>&1 | tail -1
```

## Practice challenge

Without touching the `COPY . /app` line, make `Dockerfile.before` pass `docker build --check` and keep the `notes/`
folder and the Dockerfiles out of its image.

<details>
<summary>Solution</summary>

<!-- test: contains=no warnings; contains=files in /app: package-lock.json package.json server.js; output -->
```bash
cd ~/docker-practice/lesson-034
sed -i.bak 's/^CMD node server.js$/CMD ["node", "server.js"]/' Dockerfile.before && rm Dockerfile.before.bak
printf 'notes/\nDockerfile*\nnode_modules\n' > Dockerfile.before.dockerignore
docker build --check -f Dockerfile.before . 2>&1 | tail -1
docker build -q -f Dockerfile.before -t cafe-api:before . > /dev/null
echo "files in /app: $(docker run --rm cafe-api:before ls -A /app | tr '\n' ' ')"
```

```text
Check complete, no warnings found.
files in /app: package-lock.json package.json server.js 
```

The exec form satisfies the check; an ignore file named after the Dockerfile shrinks the build context, so `COPY .`
no longer sees the notes. The image still runs as root and re-installs dependencies on every code change: the checker
does not know your intentions, which is why the review checklist matters.

</details>

## Real-world example

Teams encode these practices in tooling: `docker build --check` or Hadolint runs in CI on every Dockerfile change, a
template Dockerfile per language is shared across services, and image size and user are checked in review. Lesson 130
turns this checklist into a production Dockerfile with multi-stage builds, health checks and labels.

## Recap

- Pinned small base, dependencies before code, one clean `RUN` per concern, `.dockerignore`, non-root `USER`, exec form.
- Dependency-first ordering keeps rebuilds fast: code changes reuse the dependency layer.
- `docker build --check` catches Dockerfile mistakes without building and fails CI on warnings.
- Tools catch some problems; a review against the checklist catches the rest.

## Cleanup

<!-- test -->
```bash
docker image rm -f cafe-api:before cafe-api:after > /dev/null
rm -rf ~/docker-practice/lesson-034
```

Next: [Lesson 035 · docker build](../../05-builds/035-docker-build/README.md)
