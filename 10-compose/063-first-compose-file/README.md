# Lesson 063 · Your first Compose file

> Level 11 · Docker Compose · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

How a `compose.yaml` file is structured, how to check it before running it (`docker compose config`), and the basic
cycle: `up`, `ps`, use the application, `down`. Compose files are YAML: indentation is the structure, so most mistakes
are a few misplaced spaces.

## Visual

```text
 compose.yaml                                   what Compose creates (project "lesson-063")

 services:                                      network  lesson-063_default
   api:            ───────────────────────────▶   container lesson-063-api-1    image lesson-063-api (built)
     build: .                                      8080 on your computer ──▶ 5000 in the container
     ports: ["8080:5000"]                          env REDIS_HOST=redis
     environment: {REDIS_HOST: redis}
   redis:          ───────────────────────────▶   container lesson-063-redis-1  image redis:8-alpine
     image: redis:8-alpine

 indentation = structure: two spaces per level, never tabs
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-063 examples/python-api
cp -r 10-compose/063-first-compose-file/examples/. ~/docker-practice/lesson-063/
cd ~/docker-practice/lesson-063
ls
```

## Demonstration

Read the file: each comment explains one line.

<!-- test: contains=services; output -->
```bash
cat compose.yaml
```

```text
# compose.yaml: the cafe API and its Redis cache
services:                     # every container of the application is a service
  api:                        # service name = DNS name on the project network
    build: .                  # build the image from the Dockerfile in this folder
    ports:
      - "8080:5000"           # host port 8080 -> container port 5000
    environment:
      REDIS_HOST: redis       # the API finds Redis by its service name
  redis:
    image: redis:8-alpine     # use an existing image, no build
```

Before starting anything, let Compose validate the file and print it fully resolved (defaults added, paths absolute):

<!-- test: contains=lesson-063_default; output=head:12 -->
```bash
docker compose config --services
docker compose config | grep -E "name:|image:|target:|published:"
```

```text
api
redis
name: lesson-063
        target: 5000
        published: "8080"
    image: redis:8-alpine
    name: lesson-063_default
```

Start the application, check its state, use it:

<!-- test: contains=running; output -->
```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose ps --format '{{.Service}}: {{.State}}  {{.Ports}}'
```

```text
api: running  0.0.0.0:8080->5000/tcp, [::]:8080->5000/tcp
redis: running  6379/tcp
```

<!-- test: retry=15; contains=visits; output -->
```bash
curl -s localhost:8080/visits
curl -s localhost:8080/visits
```

```text
{"visits":1}
{"visits":2}
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker compose config` | validate the file and print the resolved configuration |
| `docker compose config --services` | only the service names |
| `docker compose up -d` | create and start everything in the background |
| `--build --quiet-build` | build the images first, without printing the build log |
| `docker compose ps` | the project's containers, with `--format` like `docker ps` |
| `docker compose down` | stop and remove the containers and the network |
| `-f FILE` | use another file than `compose.yaml` |

## Hands-on lab

**Instructions.** Add a `GREETING` variable with the value `Hello from Compose` to the `api` service, apply it with
`docker compose up -d`, and check the API's `/` endpoint.

**Expected result.** Compose recreates only the `api` container; `/` answers with your greeting.

**Verification.**

<!-- test: retry=15; contains=Hello from Compose -->
```bash
cd ~/docker-practice/lesson-063
awk '{ print } /REDIS_HOST: redis/ { print "      GREETING: Hello from Compose" }' compose.yaml > compose.new
mv compose.new compose.yaml
docker compose up -d 2> /dev/null
curl -s localhost:8080/
```

(`awk` copies every line and adds the new one after `REDIS_HOST`; editing the file in your editor is just as good.)

## Break it

A colleague's version of the file has one space too many before `environment:`:

<!-- test: fail; contains=did not find expected key; output -->
```bash
docker compose -f broken/compose.yaml config 2>&1
```

```text
yaml: while parsing a block mapping at line 2, column 5: line 5, column 6: did not find expected key
```

## Troubleshoot it

The error comes from the YAML parser, before Compose looks at any service. It names two places: the mapping it was
reading (line 2, the keys of `api`) and where it got lost (line 5, column 6). Look at those lines with visible spaces:

<!-- test: contains=environment; output -->
```bash
sed -n '2,6p' broken/compose.yaml | sed 's/ /·/g'
```

```text
··api:
····build:·.
····ports:
······-·"8080:5000"
·····environment:
```

`build` and `ports` start at column 5; `environment` starts at column 6. Keys of the same mapping must line up exactly.

## Fix it

Indent `environment:` like its siblings, and validate again:

<!-- test: contains=api -->
```bash
sed -i.bak 's/^     environment:/    environment:/' broken/compose.yaml && rm broken/compose.yaml.bak
docker compose -f broken/compose.yaml config --services
```

Run `docker compose config` after every edit: it catches syntax and schema errors before anything starts. Editors
with YAML support (and the Compose schema) mark these mistakes as you type.

## Practice challenge

Add a third service `cache-ui` to `compose.yaml` that only runs `redis-cli -h redis ping` with the `redis:8-alpine`
image, start it, and show its output.

<details>
<summary>Solution</summary>

<!-- test: contains=PONG; output -->
```bash
cd ~/docker-practice/lesson-063
cat >> compose.yaml <<'EOF'
  cache-ui:
    image: redis:8-alpine
    command: redis-cli -h redis ping
EOF
docker compose up -d 2> /dev/null
sleep 2
docker compose logs --no-log-prefix cache-ui
```

```text
PONG
```

`command:` replaces the image's default command. The new service joins the project network, so `redis` resolves. It
exits after the ping: not every service is a long-running server.

</details>

## Real-world example

Teams keep `compose.yaml` at the root of the repository and run `docker compose config` in CI (or in a pre-commit
hook), so a broken file is rejected in the pull request instead of breaking every developer's environment after the
merge.

## Recap

- `compose.yaml` lists services; each one uses an `image:` or a `build:`, plus ports, environment and more.
- Indentation is structure: keys of one mapping line up; never use tabs.
- `docker compose config` validates and shows the resolved file; use it after every edit.
- `up -d` → `ps` → use → `down`.

## Cleanup

<!-- test -->
```bash
cd ~/docker-practice/lesson-063
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-063
```

The lab folder is gone: go back to the course folder (`cd` to where you cloned the course) before the next lesson.

Next: [Lesson 064 · Services](../064-compose-services/README.md)
