# Lesson 037 · .dockerignore

> Level 6 · Docker builds · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

A `.dockerignore` file at the root of the build context lists files the builder must **never** see. `COPY . .` then
copies everything except them. It keeps three kinds of files out of images: **secrets** (`.env`, keys), **junk**
(logs, `.git`, editor folders) and **things the image builds itself** (`node_modules`, `dist/`). The syntax looks like
`.gitignore`, with one important difference you will hit in Break it.

## Visual

```text
  build context (lesson-037/)            .dockerignore                     what COPY . . sees
 ┌───────────────────────────┐      ┌──────────────────────┐          ┌───────────────────────┐
 │ server.js  package.json   │      │ .env                 │          │ server.js             │
 │ .env  (API token!)        │ ───▶ │ node_modules         │ ───────▶ │ package.json          │
 │ node_modules/  (local)    │      │ **/*.log             │  filter  │                       │
 │ logs/debug/app.log        │      │ Dockerfile*          │          │ (secrets, junk and    │
 │ Dockerfile                │      │ .dockerignore        │          │  local deps excluded) │
 └───────────────────────────┘      └──────────────────────┘          └───────────────────────┘
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-037 examples/node-api
cp 05-builds/037-dockerignore/examples/* ~/docker-practice/lesson-037/
cd ~/docker-practice/lesson-037
printf 'API_TOKEN=example-token-change-me\n' > .env
mkdir -p node_modules/left-pad logs/debug
echo "module.exports = () => 'local copy'" > node_modules/left-pad/index.js
echo "debug output" > logs/debug/app.log
ls -a
```

The lab folder now looks like a real project: a `.env` with a (fake) API token, a local `node_modules/`, and logs.
The Dockerfile uses `COPY . .`.

## Demonstration

Build without a `.dockerignore` and look inside the image:

<!-- test: contains=.env; output -->
```bash
docker build -q -t ignore-demo:before . > /dev/null
docker run --rm ignore-demo:before ls -a /app
```

```text
.
..
.env
Dockerfile
dockerignore.example
logs
node_modules
package-lock.json
package.json
server.js
```

Everything was copied. The worst one:

<!-- test: contains=API_TOKEN; output -->
```bash
docker run --rm ignore-demo:before cat /app/.env
```

```text
API_TOKEN=example-token-change-me
```

Anyone who can pull this image can read the token, even after you delete the container: it is part of an image layer
(lesson 083). Now add a `.dockerignore`:

<!-- test: absent=.env; output -->
```bash
printf '.env\nnode_modules\nlogs\nDockerfile*\ndockerignore.example\n.dockerignore\n' > .dockerignore
docker build -q -t ignore-demo:after . > /dev/null
docker run --rm ignore-demo:after ls -a /app
```

```text
.
..
package-lock.json
package.json
server.js
```

Only what the application needs. The `Dockerfile` and `.dockerignore` can be ignored too: the builder reads them
separately, `COPY` just does not copy them.

## Command breakdown

| Pattern | Matches |
|---|---|
| `.env` | the file `.env` at the root of the context |
| `node_modules` | the folder `node_modules` at the root, and everything inside it |
| `*.log` | `.log` files **at the root only** |
| `**/*.log` | `.log` files in any folder |
| `!README.md` | an exception: include it even if an earlier pattern excluded it |
| `# comment` | a comment line |

## Hands-on lab

**Instructions.** Replace the `.dockerignore` with the course's full example (`dockerignore.example`), rebuild as
`ignore-demo:lab`, and check that neither `.env` nor `node_modules` nor any log is in the image, while the API still
starts.

**Expected result.** `/app` contains only `package.json`, `package-lock.json` and `server.js`, and the server logs
`node-api listening on port 3000`.

**Verification.**

<!-- test: contains=node-api listening; absent=.env -->
```bash
cd ~/docker-practice/lesson-037
cp dockerignore.example .dockerignore
docker build -q -t ignore-demo:lab . > /dev/null
docker run --rm ignore-demo:lab ls -a /app
docker run -d --name ignore-api ignore-demo:lab > /dev/null
sleep 1
docker logs ignore-api
docker rm -f ignore-api > /dev/null
```

## Break it

A teammate writes their own short `.dockerignore`, expecting `*.log` to exclude every log file, as it would in
`.gitignore`:

<!-- test: contains=app.log; output -->
```bash
cd ~/docker-practice/lesson-037
printf '.env\nnode_modules\n*.log\n' > .dockerignore
docker build -q -t ignore-demo:logs . > /dev/null
docker run --rm ignore-demo:logs find /app/logs -type f
```

```text
/app/logs/debug/app.log
```

## Troubleshoot it

The log file is in the image although `*.log` is in `.dockerignore`. The rules differ from Git's: in `.gitignore` a
pattern without a slash matches at any depth, but in `.dockerignore` **every pattern is anchored at the root of the
context**. `*.log` therefore means "`.log` files directly in the context root", and `logs/debug/app.log` does not match.
To see exactly what a `.dockerignore` lets through, list the image (or a throw-away `COPY . .` image) as above, and
compare with the folder:

<!-- test: contains=app.log -->
```bash
find . -name '*.log'
```

## Fix it

Use `**` for "any number of folders":

<!-- test: contains=no log files -->
```bash
printf '.env\nnode_modules\n**/*.log\n' > .dockerignore
docker build -q -t ignore-demo:logs . > /dev/null
[ -z "$(docker run --rm ignore-demo:logs find /app -name '*.log')" ] && echo "no log files in the image"
```

## Practice challenge

Write an **allowlist** `.dockerignore`: exclude everything (`*`), then include only `server.js` and `package.json`
with `!` exceptions. Build `ignore-demo:allow` and show that `/app` contains exactly those two files.

<details>
<summary>Solution</summary>

<!-- test: contains=server.js; absent=node_modules; output -->
```bash
cd ~/docker-practice/lesson-037
printf '*\n!server.js\n!package.json\n' > .dockerignore
docker build -q -t ignore-demo:allow . > /dev/null
docker run --rm ignore-demo:allow ls /app
```

```text
package.json
server.js
```

An allowlist is the safest form: a new file (a key someone drops into the folder) is excluded until you deliberately
add it. The trade-off: you must remember to add every new source folder.

</details>

## Real-world example

Teams treat `.dockerignore` as a security file and review it like one: it always excludes `.env`, `*.pem`, `.git`
(which can contain old secrets in its history) and local dependency folders. Secret scanners in CI (lesson 137) catch
keys that slip into images anyway, but by then the image may already be in a registry.

## Recap

- `.dockerignore` sits at the root of the context and excludes files from `COPY`/`ADD`.
- Exclude secrets, junk and anything the image builds itself (`node_modules`, `dist/`).
- Patterns are anchored at the context root: use `**/` to match at any depth.
- An allowlist (`*` plus `!` exceptions) is the safest form.

## Cleanup

<!-- test -->
```bash
docker image rm -f ignore-demo:before ignore-demo:after ignore-demo:lab ignore-demo:logs ignore-demo:allow > /dev/null
rm -rf ~/docker-practice/lesson-037
```

Next: [Lesson 038 · Build layers](../038-build-layers/README.md)
