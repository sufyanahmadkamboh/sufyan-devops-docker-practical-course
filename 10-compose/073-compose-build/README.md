# Lesson 073 · Building images with Compose

> Level 11 · Docker Compose · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A service with `build:` gets its image from a Dockerfile. Compose builds it when the image does not exist yet, and only
then: after you change the code, `docker compose up` keeps running the **old** image until you rebuild it
(`docker compose build`, or `up --build`). The `build:` section also sets the context, the Dockerfile, build arguments
and, with `image:`, the name of the result.

## Visual

```text
 compose.yaml                                   docker compose build            docker compose up -d
 api:                                            │                               │
   build:                                        ▼                               ▼
     context: .          ──── files ────▶   BuildKit: Dockerfile ──▶ image cafe-api:1.4.0 ──▶ container
     dockerfile: Dockerfile                        ARG APP_VERSION=1.4.0
     args: {APP_VERSION: "1.4.0"}
   image: cafe-api:1.4.0

 change app.py ──▶ up -d            ──▶ image exists ──▶ OLD code keeps running ✗
 change app.py ──▶ up -d --build    ──▶ rebuild (cache: only changed layers) ──▶ new code ✓
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-073 examples/python-api
cp -r 10-compose/073-compose-build/examples/. ~/docker-practice/lesson-073/
cd ~/docker-practice/lesson-073
cat compose.yaml
```

## Demonstration

Build the images of the project (only services with `build:`) and look at the result:

<!-- test: contains=cafe-api; output -->
```bash
docker compose build --quiet 2> /dev/null
docker image ls cafe-api --format '{{.Repository}}:{{.Tag}}  {{.Size}}'
```

```text
cafe-api:1.4.0  223MB
```

The build argument reached the image:

<!-- test: contains=APP_VERSION=1.4.0; output -->
```bash
docker compose up -d 2> /dev/null
docker compose exec api printenv APP_VERSION | sed 's/^/APP_VERSION=/'
```

```text
APP_VERSION=1.4.0
```

`docker compose images` shows which image each container of the project runs:

<!-- test: contains=cafe-api; output -->
```bash
docker compose images --format json | grep -o '"Repository":"[^"]*","Tag":"[^"]*"' | sort -u
```

```text
"Repository":"cafe-api","Tag":"1.4.0"
"Repository":"redis","Tag":"8-alpine"
```

## Command breakdown

| Key / command | What it does |
|---|---|
| `build: .` | short form: the context folder, `Dockerfile` inside it |
| `build: {context, dockerfile, args, target}` | long form; `target` picks a stage of a multi-stage build (lesson 087) |
| `image:` next to `build:` | the name of the built image (and what `push` uploads) |
| `docker compose build [SERVICE]` | build (or rebuild) the images |
| `docker compose up -d --build` | rebuild, then recreate containers whose image changed |
| `docker compose build --no-cache` | ignore the build cache (lesson 039) |
| `docker compose images` | the images used by the project's containers |

## Hands-on lab

**Instructions.** Build a second version with `APP_VERSION=1.5.0` without editing `compose.yaml`, using
`docker compose build --build-arg`, and check the variable in a one-off container.

**Expected result.** `1.5.0`. (The image keeps its name `cafe-api:1.4.0` from the file: a reason to take the tag from a
variable, as the challenge does.)

**Verification.**

<!-- test: contains=1.5.0 -->
```bash
cd ~/docker-practice/lesson-073
docker compose build --quiet --build-arg APP_VERSION=1.5.0 api 2> /dev/null
docker compose run --rm --no-deps api printenv APP_VERSION 2> /dev/null
```

Back to 1.4.0:

<!-- test -->
```bash
docker compose build --quiet 2> /dev/null
docker compose up -d 2> /dev/null
```

## Break it

A developer changes the API's default greeting and restarts the stack:

<!-- test: contains=Hello from Python; output -->
```bash
sed -i.bak 's/Hello from Python/Hello from version 1.4.0/' app.py && rm app.py.bak
grep -c "Hello from version 1.4.0" app.py
docker compose up -d 2> /dev/null
sleep 2
curl -s localhost:8080/
```

```text
1
{"hostname":"d866db03be30","message":"Hello from Python"}
```

## Troubleshoot it

The file is changed, the answer is old. The code inside an image is a copy made at build time (`COPY app.py .`), and
`up` reuses the existing image. Compare the image's creation time with the file:

<!-- test: contains=Hello from Python; output -->
```bash
docker image inspect cafe-api:1.4.0 --format 'image built: {{.Created}}'
docker compose exec api grep -o "Hello from [A-Za-z0-9. ]*" app.py
```

```text
image built: 2026-10-05T17:11:02.737714484Z
Hello from Python
```

The container runs the code of the image, which still has the old `app.py`.

## Fix it

<!-- test: retry=15; contains=Hello from version 1.4.0; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
curl -s localhost:8080/
```

```text
{"hostname":"74c930a4170b","message":"Hello from version 1.4.0"}
```

The rebuild was fast: `requirements.txt` did not change, so the `pip install` layer came from the cache, and only the
`COPY app.py` layer and the ones after it were rebuilt (lesson 039). For fast feedback during development, Compose can
also sync or rebuild automatically (`docker compose watch`, with a `develop:` section).

## Practice challenge

Make the image tag configurable: change `image:` to `cafe-api:${APP_VERSION:-dev}` and the build argument to
`${APP_VERSION:-dev}`, then build version `2.0.0` from the command line only.

<details>
<summary>Solution</summary>

<!-- test: contains=cafe-api:2.0.0; output -->
```bash
cd ~/docker-practice/lesson-073
sed -i.bak -e 's/image: cafe-api:1.4.0/image: cafe-api:${APP_VERSION:-dev}/' \
           -e 's/APP_VERSION: "1.4.0"/APP_VERSION: "${APP_VERSION:-dev}"/' compose.yaml && rm compose.yaml.bak
APP_VERSION=2.0.0 docker compose build --quiet 2> /dev/null
docker image ls cafe-api --format '{{.Repository}}:{{.Tag}}' | sort
```

```text
cafe-api:1.4.0
cafe-api:2.0.0
```

One variable now sets both the version inside the image and its tag: CI pipelines pass the Git tag or commit here.

</details>

## Real-world example

A CI pipeline runs `APP_VERSION=$GIT_TAG docker compose build` and `docker compose push` (lesson 076), so the images in
the registry are tagged with the release. Developers, meanwhile, use `docker compose up --build` (or `watch`) to make
sure they never test yesterday's image. A common surprise in code review is "it works for me" from someone who forgot
to rebuild.

## Recap

- `build:` builds an image for a service; `image:` names it.
- Compose builds only when the image is missing: after code changes, use `up --build` or `build`.
- `args:` pass build arguments (`ARG`); `target:` selects a stage.
- The build cache keeps rebuilds fast when the Dockerfile is ordered well.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-073
docker compose down -v 2> /dev/null
docker image rm -f cafe-api:1.4.0 cafe-api:1.5.0 cafe-api:2.0.0 > /dev/null 2>&1
rm -rf ~/docker-practice/lesson-073
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 074 · up, down and the project lifecycle](../074-compose-up-down/README.md)
