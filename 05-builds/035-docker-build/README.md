# Lesson 035 · docker build

> Level 6 · Docker builds · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`docker build` turns a **Dockerfile** and a folder of files (the **build context**) into an **image**. The Docker CLI
sends the context to the builder (BuildKit), the builder runs the Dockerfile's instructions one by one, and the result
is stored as an image with the name and tag you give it with `-t`. This lesson covers the command itself: naming,
tagging, choosing the Dockerfile, and reading the build output.

## Visual

```text
  ~/docker-practice/lesson-035                docker build -t node-api:1.0 .
 ┌──────────────────────────┐                                 │
 │ Dockerfile               │ ── instructions ──┐             │  "." = the build context
 │ package.json  server.js  │ ── context ───────┤             ▼
 └──────────────────────────┘                   ▼     ┌──────────────────────┐
                                        BuildKit runs │ FROM node:24-alpine  │ ─▶ layer
                                        each step     │ WORKDIR /app         │ ─▶ layer
                                                      │ COPY package.json …  │ ─▶ layer
                                                      │ EXPOSE / CMD         │ ─▶ metadata
                                                      └──────────┬───────────┘
                                                                 ▼
                                                     image  node-api:1.0  (in the local image store)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-035 examples/node-api
cp 05-builds/035-docker-build/examples/Dockerfile ~/docker-practice/lesson-035/
cd ~/docker-practice/lesson-035
ls
cat Dockerfile
```

A small Node.js API (`server.js`, no dependencies) and a five-line Dockerfile: start from the official Node.js 24 image,
work in `/app`, copy the two files, document port 3000, and start the server.

## Demonstration

Build the image. `-t` gives it a name and a tag; the final `.` is the build context (the current folder):

<!-- test: contains=naming to; output -->
```bash
docker build -t node-api:1.0 . 2>&1 | grep -E '^#[0-9]+ \[|naming to|DONE' | tail -8
```

```text
#5 [1/3] FROM docker.io/library/node:24-alpine@sha256:ebfe2f90462722a7a4de65e91990e97fe0d401c70e0e762c5b53302f905ec1c1
#5 DONE 0.1s
#6 [2/3] WORKDIR /app
#6 DONE 0.0s
#7 [3/3] COPY package.json server.js ./
#7 DONE 0.0s
#8 naming to docker.io/library/node-api:1.0 done
#8 DONE 0.3s
```

Each `#N [x/3]` line is one Dockerfile step. `naming to docker.io/library/node-api:1.0` is the result: a short name like
`node-api` is expanded to Docker Hub's `docker.io/library/` namespace (lesson 077). The image is now in the local store:

<!-- test: contains=node-api; output -->
```bash
docker image ls node-api
```

```text
IMAGE          ID             DISK USAGE   CONTENT SIZE   EXTRA
node-api:1.0   cc15be895456        241MB         61.6MB        
```

Run it, publishing the container's port 3000 on port 8080 of your computer:

<!-- test: contains=Up -->
```bash
docker run -d --name api -p 8080:3000 node-api:1.0 > /dev/null
docker ps --filter name=api --format '{{.Names}}: {{.Status}}'
```

<!-- test: retry=10; contains=Hello from Node.js; output -->
```bash
curl -s http://localhost:8080/
```

```text
{"message":"Hello from Node.js","hostname":"c1a8c165f796","version":"dev"}
```

## Command breakdown

| Command / flag | Meaning |
|---|---|
| `docker build PATH` | build an image; PATH is the build context (lesson 036) |
| `-t NAME:TAG` | name and tag the result; repeat `-t` for several tags; no tag means `latest` (lesson 021) |
| `-f FILE` | use another Dockerfile (default: `Dockerfile` in the context) |
| `-q` | quiet: print only the image ID |
| `--progress=plain` | full, line-by-line build output (the default in a terminal is a compact live view) |
| `--no-cache` | run every step again, ignoring the cache (lesson 039) |

## Hands-on lab

**Instructions.** Build the same folder a second time with **two** tags at once, `node-api:1.1` and `node-api:stable`,
and list the `node-api` images.

**Expected result.** Three tags. `1.1` and `stable` have the same image ID (one image, two names); because nothing
changed, the build was served from the cache and `1.0` has that ID too.

**Verification.**

<!-- test: contains=node-api:stable -->
```bash
cd ~/docker-practice/lesson-035
docker build -q -t node-api:1.1 -t node-api:stable . > /dev/null
docker image ls node-api
```

## Break it

A teammate renamed the Dockerfile to `Dockerfile.prod` for production and now runs the usual command:

<!-- test: fail; contains=Dockerfile; output -->
```bash
cd ~/docker-practice/lesson-035
mv Dockerfile Dockerfile.prod
docker build -t node-api:prod . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

```text
ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

## Troubleshoot it

`failed to read dockerfile: open Dockerfile: no such file or directory`: the builder looked for the default name,
`Dockerfile`, in the context, and there is none. The build never started. List what is really there:

<!-- test: contains=Dockerfile.prod; output -->
```bash
ls
```

```text
Dockerfile.prod
package-lock.json
package.json
server.js
```

## Fix it

Name the file explicitly with `-f`:

<!-- test: contains=node-api:prod -->
```bash
docker build -q -f Dockerfile.prod -t node-api:prod . > /dev/null
docker image ls node-api
```

Teams commonly keep several Dockerfiles (`Dockerfile`, `Dockerfile.dev`, `Dockerfile.test`) and choose with `-f`; the
context (`.`) stays the same.

## Practice challenge

Build the API once more as `node-api:quiet`, printing **only** the image ID (nothing else), and check that this ID is
the one `docker image inspect` reports for that tag.

<details>
<summary>Solution</summary>

<!-- test: contains=same image -->
```bash
cd ~/docker-practice/lesson-035
id=$(docker build -q -f Dockerfile.prod -t node-api:quiet .)
echo "$id"
[ "$id" = "$(docker image inspect --format '{{.Id}}' node-api:quiet)" ] && echo "same image"
```

`-q` prints the full image ID (`sha256:…`), which scripts use to refer to exactly the image they just built.

</details>

## Real-world example

A CI pipeline builds every commit with a tag that identifies it, for example
`docker build -t registry.example.com/shop/api:${GIT_SHA} -t registry.example.com/shop/api:main .`, then pushes both
tags (lessons 077, 136). The SHA tag is immutable and traceable to the code; the branch tag moves to the latest build.

## Recap

- `docker build -t NAME:TAG CONTEXT` builds an image from `CONTEXT/Dockerfile`.
- `-f` chooses another Dockerfile; several `-t` give one image several names.
- The build output lists one step per instruction and ends with `naming to …`.
- `failed to read dockerfile` means the builder found no Dockerfile under the expected name.

## Cleanup

<!-- test -->
```bash
docker rm -f api > /dev/null
docker image rm -f node-api:1.0 node-api:1.1 node-api:stable node-api:prod node-api:quiet > /dev/null
rm -rf ~/docker-practice/lesson-035
```

Next: [Lesson 036 · The build context](../036-build-context/README.md)
