# Lesson 101 · Labels

> Level 17 · Advanced Docker · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

A **label** is a key-value pair of metadata attached to an image, a container, a network or a volume. Docker itself
ignores labels; people and tools use them to answer "what is this?": which source code and version an image was built
from, which team owns a container, which environment it belongs to. Filters (`--filter label=…`) then select objects
by label for listing, monitoring or cleanup.

## Visual

```text
  Image labels (LABEL in the Dockerfile, fixed at build)      Container labels (docker run --label, per container)

  org.opencontainers.image.source   = https://github.com/…    team = payments
  org.opencontainers.image.revision = 3f2c1ab                 env  = staging
  org.opencontainers.image.version  = 1.4.0                   com.example.cost-center = 4711

            docker ps --filter label=team=payments          docker image ls --filter label=org.opencontainers.image.version=1.4.0
            docker container prune --filter label=env=test  docker system prune --filter label!=keep
```

The `org.opencontainers.image.*` keys are a standard (the OCI image specification): registries such as GitHub
Container Registry use `…source` to link an image to its repository.

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-101 16-advanced/101-labels/examples
cd ~/docker-practice/lesson-101
cat Dockerfile
```

## Demonstration

Build the image with a version and a Git revision passed as build arguments (in CI they come from the pipeline):

<!-- test: contains=cafe-web:1.4.0 -->
```bash
docker build -q --build-arg VERSION=1.4.0 --build-arg REVISION=3f2c1ab -t cafe-web:1.4.0 . > /dev/null
docker image ls cafe-web --format '{{.Repository}}:{{.Tag}}'
```

The labels are part of the image (labels of the base image are inherited too; here only the OCI ones are shown):

<!-- test: contains=org.opencontainers.image.revision=3f2c1ab; output -->
```bash
docker image inspect --format '{{range $k, $v := .Config.Labels}}{{$k}}={{$v}}{{println}}{{end}}' cafe-web:1.4.0 | grep '^org.opencontainers'
```

```text
org.opencontainers.image.description=The cafe's static website
org.opencontainers.image.licenses=MIT
org.opencontainers.image.revision=3f2c1ab
org.opencontainers.image.source=https://github.com/example/cafe-web
org.opencontainers.image.title=cafe-web
org.opencontainers.image.version=1.4.0
```

Containers get their own labels at start time:

<!-- test: contains=pay-web; contains=pay-api; absent=shop-web; output -->
```bash
docker run -d --name pay-web --label team=payments --label env=staging cafe-web:1.4.0 > /dev/null
docker run -d --name pay-api --label team=payments --label env=test alpine:3.23 sleep 300 > /dev/null
docker run -d --name shop-web --label team=shop --label env=staging cafe-web:1.4.0 > /dev/null
docker ps --filter label=team=payments --format '{{.Names}} {{.Label "env"}}'
```

```text
pay-api test
pay-web staging
```

## Command breakdown

| Command | What it does |
|---|---|
| `LABEL key="value" …` | add labels to the image (Dockerfile) |
| `docker run --label key=value` | add a label to the container |
| `docker build --label key=value` | add a label at build time without changing the Dockerfile |
| `--filter label=key` / `label=key=value` | objects that have the label / that value |
| `--filter label!=key=value` | objects without it (prune commands) |
| `{{.Label "key"}}` in `docker ps --format` | one label's value |
| `{{json .Config.Labels}}` in `docker inspect` | all labels |

## Hands-on lab

**Instructions.** List only the containers that belong to the `staging` environment, with their team.

**Expected result.** `pay-web payments` and `shop-web shop`.

**Verification.**

<!-- test: contains=pay-web payments; contains=shop-web shop; absent=pay-api -->
```bash
docker ps --filter label=env=staging --format '{{.Names}} {{.Label "team"}}'
```

## Break it

A teammate cleans up the test environment of team payments, using the key spelling from a wiki page:

<!-- test: contains=nothing to remove; output -->
```bash
found=$(docker ps -q --filter label=Team=payments --filter label=env=test)
[ -n "$found" ] && docker rm -f $found || echo "nothing to remove"
```

```text
nothing to remove
```

`pay-api` is still running.

## Troubleshoot it

Filters compare keys and values **exactly**, case included: `Team` is not `team`. Look at the container's real
labels:

<!-- test: contains="team":"payments"; output -->
```bash
docker inspect --format '{{json .Config.Labels}}' pay-api
```

```text
{"env":"test","team":"payments"}
```

## Fix it

Use the exact key. Before deleting anything selected by a filter, list it first:

<!-- test: contains=pay-api; output -->
```bash
docker ps --filter label=team=payments --filter label=env=test --format '{{.Names}}'
docker container rm -f $(docker ps -q --filter label=team=payments --filter label=env=test) > /dev/null && echo "removed"
```

```text
pay-api
removed
```

Several `--filter label=…` options must **all** match. Teams avoid this class of error by writing label keys in one
place (a Compose file, a CI template) and in a reverse-DNS style (`com.example.team`), lowercase.

## Practice challenge

Find every image on the engine that has an `org.opencontainers.image.version` label, and print its name with that
version.

<details>
<summary>Solution</summary>

<!-- test: contains=cafe-web:1.4.0 version=1.4.0; output -->
```bash
docker image ls --filter label=org.opencontainers.image.version --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' |
  while read -r image; do
    echo "$image version=$(docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.version"}}' "$image")"
  done
```

```text
cafe-web:1.4.0 version=1.4.0
ubuntu:24.04 version=24.04
```

`index` is needed because the key contains dots, which the template language would read as nested fields. Other
images may appear too: many official images (Ubuntu, for example) carry OCI labels. `grep -v '<none>'` skips untagged
images, which cannot be inspected by name.

</details>

## Real-world example

A CI pipeline adds `org.opencontainers.image.revision` (the Git commit) and `…source` to every image; when production
misbehaves, `docker image inspect` on the running image tells the on-call engineer the exact commit. Compose labels its
containers with `com.docker.compose.project` and `com.docker.compose.service`, and Traefik, a reverse proxy, reads
routing rules from container labels such as `traefik.http.routers.web.rule`.

## Recap

- Labels are key-value metadata on images (`LABEL`, `--label` at build) and containers (`docker run --label`).
- Use the `org.opencontainers.image.*` keys for source, revision, version and license.
- `--filter label=key=value` selects objects; keys and values match exactly, case included.
- List what a filter selects before you delete it.

## Cleanup

<!-- test -->
```bash
docker rm -f pay-web pay-api shop-web > /dev/null 2>&1 || true
docker image rm -f cafe-web:1.4.0 > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-101
```

Next: [Lesson 102 · Logging drivers](../102-logging-drivers/README.md)
