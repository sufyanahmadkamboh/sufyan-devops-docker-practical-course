# Lesson 036 · The build context

> Level 6 · Docker builds · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

The last argument of `docker build` is the **build context**: the folder whose files the builder may use. The CLI
sends that folder to the builder (BuildKit) before any instruction runs, and `COPY`/`ADD` can only read files from it.
Two consequences: everything in the context is transferred (big folders make builds slow), and a Dockerfile can never
copy a file from outside the context, such as `../shared/config.json`.

## Visual

```text
  docker build -t ctx-api:1.0 .            the context is "." = node-api/
                                                     │
  lesson-036/                                        ▼
  ├── node-api/   ◀── context ──────────▶  ┌───────────────────────────┐
  │   ├── Dockerfile                       │ BuildKit sees ONLY these: │
  │   ├── package.json                     │   Dockerfile              │
  │   ├── server.js                        │   package.json            │
  │   └── debug.log (50 MB) ── sent if ──▶│   server.js  debug.log    │
  └── shared/            COPY . . uses it  └───────────────────────────┘
      └── config.json   ✗ outside the context: COPY ../shared/config.json fails

  docker build -f node-api/Dockerfile.fixed .   (from lesson-036/) → the context is the whole lab folder
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-036 examples/node-api 05-builds/036-build-context/examples/shared
cp 05-builds/036-build-context/examples/Dockerfile* ~/docker-practice/lesson-036/node-api/
cd ~/docker-practice/lesson-036/node-api
ls . ../shared
```

Two folders: `node-api/` (the API and four Dockerfiles) and `shared/config.json`, a configuration file another team
maintains next to the API.

## Demonstration

Build from inside `node-api/`. Near the start, the builder loads the context; the `transferring context` line tells you
how much was sent:

<!-- test: contains=transferring context; output -->
```bash
docker build --no-cache -t ctx-api:1.0 . 2>&1 | grep 'transferring context' | tail -1
```

```text
#5 transferring context: 1.00kB done
```

About a kilobyte: the two small files. Now someone leaves a 50 MB log file in the folder (`head -c` writes 50 million
zero bytes, standing in for a real log, a dataset or `node_modules`) and builds again:

<!-- test: contains=transferring context; output -->
```bash
head -c 50000000 /dev/zero > debug.log
docker build --no-cache -t ctx-api:1.0 . 2>&1 | grep 'transferring context' | tail -1
```

```text
#4 transferring context: 63B done
```

Still tiny: BuildKit reads the Dockerfile first and only transfers the paths that `COPY` and `ADD` name, here
`package.json` and `server.js`. Most Dockerfiles, however, contain `COPY . .` ("copy the whole context"), like
`Dockerfile.all`:

<!-- test: contains=transferring context; output -->
```bash
cat Dockerfile.all
docker build --no-cache -f Dockerfile.all -t ctx-api:all . 2>&1 | grep 'transferring context' | tail -1
```

```text
FROM node:24-alpine
WORKDIR /app
COPY . .
CMD ["node", "server.js"]
#4 transferring context: 50.01MB 2.2s done
```

Now the 50 MB are transferred **and** baked into the image, where nobody needs them:

<!-- test: contains=debug.log; output -->
```bash
docker run --rm ctx-api:all ls -lh /app/debug.log
docker image ls ctx-api
```

```text
-rwxr-xr-x    1 root     root       47.7M Oct  5 17:04 /app/debug.log
IMAGE         ID             DISK USAGE   CONTENT SIZE   EXTRA
ctx-api:1.0   84ce4416dac7        241MB         61.6MB        
ctx-api:all   a4dab8d30d2b        292MB         61.7MB        
```

On a remote builder (CI, `docker buildx` with a cloud builder) every unneeded megabyte also travels over the network.
Lesson 037 shows how to exclude files with `.dockerignore`; for now, delete the log:

<!-- test -->
```bash
rm debug.log
```

## Command breakdown

| Part | Meaning |
|---|---|
| `docker build … .` | the context is the current folder |
| `docker build … ../..` / `… /path/to/dir` | any folder can be the context |
| `-f node-api/Dockerfile.fixed` | the Dockerfile may live anywhere; `COPY` paths stay relative to the context |
| `transferring context: N` | how much of the context was sent (only the paths `COPY`/`ADD` need) |
| `--no-cache` | run every step again (used here so each build reports its context) |

## Hands-on lab

**Instructions.** From inside `node-api/`, build with the **parent** folder (`..`) as the context and
`Dockerfile` from the current folder (`-f Dockerfile`). Why does it fail?

**Expected result.** The build fails on `COPY package.json server.js`: these paths are relative to the context
(`..`), where the files are at `node-api/package.json` and `node-api/server.js`.

**Verification.**

<!-- test: fail; contains=not found -->
```bash
cd ~/docker-practice/lesson-036/node-api
docker build -f Dockerfile -t ctx-api:parent .. 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

## Break it

Now the API needs `shared/config.json`. A teammate adds `COPY ../shared/config.json ./config.json` to the Dockerfile
(`Dockerfile.config`) and builds from `node-api/` as usual:

<!-- test: fail; contains=not found; output -->
```bash
cd ~/docker-practice/lesson-036/node-api
docker build -f Dockerfile.config -t ctx-api:config . 2>&1 | grep ERROR
test "${PIPESTATUS[0]}" -eq 0
```

```text
#7 ERROR: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::kop341gts9ld444k5tr57om0z: "/shared/config.json": not found
ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::kop341gts9ld444k5tr57om0z: "/shared/config.json": not found
```

## Troubleshoot it

`"/shared/config.json": not found` although the file clearly exists on disk. Look at the path in the message: the
builder turned `../shared/config.json` into `/shared/config.json`, a path at the **root of the context**. A build can
never leave its context: `..` stops at the top of it, for security (a Dockerfile from the internet must not be able to
read `~/.ssh`) and because the context is all the builder received. The file exists, but not in the context:

<!-- test: contains=../shared/config.json -->
```bash
ls ../shared/config.json
ls ./shared/config.json 2>&1 || true
```

## Fix it

Make the context the folder that contains **both** directories, and write the `COPY` paths relative to it.
`Dockerfile.fixed` does exactly that:

<!-- test: contains=COPY shared/config.json; output -->
```bash
cd ~/docker-practice/lesson-036
grep COPY node-api/Dockerfile.fixed
```

```text
COPY node-api/package.json node-api/server.js ./
COPY shared/config.json ./config.json
```

<!-- test: contains=new_menu; output -->
```bash
docker build -q -f node-api/Dockerfile.fixed -t ctx-api:config . > /dev/null
docker run --rm ctx-api:config cat /app/config.json
```

```text
{
  "feature_flags": { "new_menu": true }
}
```

The other option is to copy the file into `node-api/` before building (CI pipelines often assemble a context folder).
What never works is reaching outside the context.

## Practice challenge

Prove that the builder only ever sees the context: create a file `../secret-note.txt` next to the lab folder, then try
to `COPY` it with `COPY ../../secret-note.txt ./` in a throw-away Dockerfile read from standard input
(`docker build -f - .`). The build must fail.

<details>
<summary>Solution</summary>

<!-- test: fail; contains=not found; output -->
```bash
cd ~/docker-practice/lesson-036/node-api
echo "not for images" > ../../secret-note.txt
printf 'FROM alpine:3.23\nCOPY ../../secret-note.txt ./\n' | docker build -f - -t ctx-api:secret . 2>&1 | grep -o '"/secret-note.txt": not found' | head -1
test "${PIPESTATUS[1]}" -eq 0
```

```text
"/secret-note.txt": not found
```

`-f -` reads the Dockerfile from standard input; the context is still `.`. However many `../` you write, the path is
resolved inside the context: files next to it are out of reach.

</details>

## Real-world example

In a monorepo, a service often needs shared code (`libs/common/`). Teams build each service with the repository root
as the context and a per-service Dockerfile: `docker build -f services/orders/Dockerfile -t orders:1.4 .`. The
`.dockerignore` at the root (lesson 037) keeps the transfer small, because a repository root can contain gigabytes of
other services, test data and `.git`.

## Recap

- The context is the folder given to `docker build`; it is sent to the builder before the build starts.
- `COPY` and `ADD` can only read files inside the context; `../` cannot leave it.
- BuildKit transfers what `COPY`/`ADD` name; `COPY . .` sends (and bakes in) everything: check `transferring context`.
- To use files from several folders, make their common parent the context and select the Dockerfile with `-f`.

## Cleanup

<!-- test -->
```bash
docker image rm -f ctx-api:1.0 ctx-api:all ctx-api:config > /dev/null
rm -rf ~/docker-practice/lesson-036 ~/docker-practice/secret-note.txt
```

Next: [Lesson 037 · .dockerignore](../037-dockerignore/README.md)
