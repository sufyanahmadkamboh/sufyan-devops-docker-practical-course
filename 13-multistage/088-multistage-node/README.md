# Lesson 088 · Multi-stage builds for Node.js

> Level 14 · Multi-stage builds · ⏱ 25 minutes · run every command from the course folder

## What are we learning?

A Node.js service written in TypeScript (or with a bundler, a frontend framework, test tools) needs **development
dependencies** to build, and only **production dependencies** plus the compiled JavaScript to run. A two-stage
Dockerfile installs everything and compiles in the first stage, then starts the final stage fresh: `npm ci --omit=dev`
and `COPY --from=build /app/dist`. The TypeScript compiler, the type definitions and the `.ts` sources never reach the
image.

## Visual

```text
  ts-api/                         stage "build" (node:24-alpine)          final stage (node:24-alpine)
  ├── package.json         ──▶    npm ci              (typescript,        npm ci --omit=dev   (production
  ├── package-lock.json             @types/node, …: devDependencies)        dependencies only: none here)
  ├── tsconfig.json        ──▶    npm run build  → tsc                    COPY --from=build /app/dist ./dist
  └── src/server.ts        ──▶    /app/dist/server.js  ─────────────────▶ /app/dist/server.js
                                  /app/node_modules  (≈ 25 MB)  ✗ stays   USER node
                                  /app/src/*.ts                 ✗ behind  CMD ["node", "dist/server.js"]
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-088 13-multistage/088-multistage-node/examples/ts-api
cp 13-multistage/088-multistage-node/examples/Dockerfile* ~/docker-practice/lesson-088/
cd ~/docker-practice/lesson-088
cat package.json
```

A TypeScript version of the course API. `typescript` and `@types/node` are `devDependencies`: needed to compile, not
to run.

## Demonstration

Build the single-stage and the multi-stage version:

<!-- test: contains=ts-multi; output -->
```bash
docker build -q -f Dockerfile.single -t ts-single:1.0 . > /dev/null
docker build -q -t ts-multi:1.0 . > /dev/null
docker image ls --filter 'reference=ts-*' --format '{{.Repository}}:{{.Tag}}\t{{.Size}}'
```

```text
ts-multi:1.0	245MB
ts-single:1.0	289MB
```

Look inside both: the single-stage image carries the compiler and the sources, the multi-stage one only the output:

<!-- test: contains=typescript; output -->
```bash
echo "single: $(docker run --rm ts-single:1.0 ls /app /app/node_modules | tr '\n' ' ')"
echo "multi:  $(docker run --rm ts-multi:1.0 ls /app | tr '\n' ' ')"
```

```text
single: /app: dist node_modules package-lock.json package.json src tsconfig.json  /app/node_modules: @types typescript undici-types 
multi:  dist package-lock.json package.json 
```

<!-- test: contains=Up -->
```bash
docker run -d --name ts-multi -p 8090:3000 ts-multi:1.0 > /dev/null
docker ps --filter name=ts-multi --format '{{.Names}}: {{.Status}}'
```

<!-- test: retry=10; contains=Hello from TypeScript; output -->
```bash
curl -s http://localhost:8090/
```

```text
{"message":"Hello from TypeScript","hostname":"a4e3b468b625"}
```

The base image (`node:24-alpine`, the Node.js runtime) is most of both images; what multi-stage removes is everything
the project added only for building. In a real project with a bundler, test framework and linters, that is often
hundreds of MB.

## Command breakdown

| Step | Why |
|---|---|
| `FROM node:24-alpine AS build` + `npm ci` | install production **and** development dependencies to build |
| `RUN npm run build` | compile TypeScript to `dist/` |
| second `FROM node:24-alpine` | a clean start: nothing from the build stage unless copied |
| `npm ci --omit=dev` | production dependencies only, from the same lockfile |
| `COPY --from=build /app/dist ./dist` | the only thing taken from the build stage |

## Hands-on lab

**Instructions.** Count the packages in `node_modules` of the build stage and of the final image. Build the stage with
`--target build`.

**Expected result.** The build stage has the TypeScript packages; the final image has an empty (or no) `node_modules`,
because this API has no production dependencies.

**Verification.**

<!-- test: contains=final: 0 -->
```bash
docker build -q --target build -t ts-multi:build . > /dev/null
echo "build: $(docker run --rm ts-multi:build sh -c 'ls node_modules | wc -l') packages"
echo "final: $(docker run --rm ts-multi:1.0 sh -c 'ls node_modules 2>/dev/null | wc -l') packages"
```

## Break it

`Dockerfile.broken` is the multi-stage Dockerfile with one line missing. It builds without any error:

<!-- test: contains=ts-multi:broken -->
```bash
docker build -q -f Dockerfile.broken -t ts-multi:broken . > /dev/null
docker image ls --filter 'reference=ts-multi' --format '{{.Repository}}:{{.Tag}}'
```

But the container does not stay up:

<!-- test: contains=Exited; output -->
```bash
docker run -d --name ts-broken ts-multi:broken > /dev/null
sleep 2
docker ps -a --filter name=ts-broken --format '{{.Names}}: {{.Status}}'
```

```text
ts-broken: Exited (1) 2 seconds ago
```

## Troubleshoot it

The build cannot catch a missing file in the final stage: every instruction succeeded. The container's log can:

<!-- test: contains=Cannot find module; output -->
```bash
docker logs ts-broken 2>&1 | grep -E '^Error'
```

```text
Error: Cannot find module '/app/dist/server.js'
```

`dist/` was built in the build stage and never copied into the final one. Compare the two Dockerfiles:

<!-- test: contains=COPY --from=build -->
```bash
diff Dockerfile.broken Dockerfile || true
```

## Fix it

Restore the `COPY --from=build /app/dist ./dist` line (it is in `Dockerfile`) and check that the image really starts.
A quick smoke test after every build catches this class of mistake:

<!-- test: contains=ts-api listening -->
```bash
docker rm -f ts-broken > /dev/null
docker build -q -t ts-multi:fixed . > /dev/null
docker run -d --name ts-fixed ts-multi:fixed > /dev/null
sleep 1
docker logs ts-fixed
docker rm -f ts-fixed > /dev/null
```

## Practice challenge

The build stage is useful during development too: build only it, then run the TypeScript compiler's type check
(`npx tsc --noEmit`) inside it, without creating a final image.

<details>
<summary>Solution</summary>

<!-- test: contains=types ok; output -->
```bash
cd ~/docker-practice/lesson-088
docker build -q --target build -t ts-multi:build . > /dev/null
docker run --rm ts-multi:build sh -c 'npx tsc --noEmit && echo "types ok"'
```

```text
types ok
```

The final image could not do this: it has no TypeScript. CI pipelines run checks like this against the build stage
(`--target build`) and ship the final stage.

</details>

## Real-world example

A React or Vue frontend uses the same pattern with a different final stage: `FROM node:24-alpine AS build` runs
`npm ci && npm run build`, and the final stage is `FROM nginx:1.30-alpine` with
`COPY --from=build /app/dist /usr/share/nginx/html`. No Node.js at all in the shipped image, only a web server and
static files. The capstone (module 22) builds its frontend this way.

## Recap

- Build stage: all dependencies + compile; final stage: production dependencies + compiled output.
- `npm ci --omit=dev` in the final stage keeps development tools out.
- A missing `COPY --from` builds fine and fails at run time: smoke-test every image you build.
- `--target build` gives a stage with the full toolchain for checks and debugging.

## Cleanup

<!-- test -->
```bash
docker rm -f ts-multi ts-broken ts-fixed > /dev/null 2>&1 || true
docker image rm -f ts-single:1.0 ts-multi:1.0 ts-multi:build ts-multi:broken ts-multi:fixed > /dev/null 2>&1 || true
rm -rf ~/docker-practice/lesson-088
```

Next: [Lesson 089 · Multi-stage builds for Go](../089-multistage-go/README.md)
