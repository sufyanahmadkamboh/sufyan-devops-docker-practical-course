# Lesson 022 · Your first Dockerfile

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

A **Dockerfile** is a text file with the recipe for an image: start from a base image, add files, run commands, and
say what the container runs. `docker build` follows the recipe step by step and produces an image. Because the recipe
is a file, it lives in Git next to the code: every image can be rebuilt, reviewed and changed like code.

## Visual

```text
  Dockerfile                                  docker build -t cafe-site:1.0 .

  FROM nginx:1.30-alpine        ──────▶  layer: the base image (Alpine + Nginx)
  COPY . /usr/share/nginx/html/ ──────▶  layer: the website's files
  EXPOSE 80                     ──────▶  metadata: the port the app listens on
  CMD ["nginx", "-g", "daemon off;"] ─▶  metadata: what a container runs
                                                │
                                                ▼
                                      image cafe-site:1.0 ──▶ docker run -p 8080:80 … ──▶ http://localhost:8080
```

| Instruction | Purpose | In depth |
|---|---|---|
| `FROM` | the base image every Dockerfile starts from | lesson 023 |
| `WORKDIR` | the working directory for the following instructions | lesson 024 |
| `COPY` / `ADD` | add files from the build context | lesson 025 |
| `RUN` | run a command at build time; its result becomes a layer | lesson 026 |
| `CMD` / `ENTRYPOINT` | what the container runs | lessons 027–029 |
| `ENV` / `ARG` | runtime / build-time variables | lessons 030, 031 |
| `EXPOSE` / `USER` | document the port / choose the user | lessons 032, 033 |

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-022 examples/site
cd ~/docker-practice/lesson-022
ls
```

The cafe's static website: `index.html` and `styles.css`.

## Demonstration

Write the Dockerfile next to the website:

<!-- test: contains=FROM -->
```bash
cat > Dockerfile <<'EOF'
# The cafe website, served by Nginx
FROM nginx:1.30-alpine
COPY . /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
cat Dockerfile
```

Build it. `-t` names the image, and `.` is the **build context**: the folder whose files `COPY` can use (lesson 036):

<!-- test: contains=naming to; output -->
```bash
docker build -t cafe-site:1.0 . 2>&1 | grep -E '^#[0-9]+ \[|naming to'
```

```text
#1 [internal] load build definition from Dockerfile
#2 [internal] load metadata for docker.io/library/nginx:1.30-alpine
#3 [internal] load .dockerignore
#4 [1/2] FROM docker.io/library/nginx:1.30-alpine@sha256:0985e772fb9f729e6fa0980da05fca5d9c468e870eed43071545afa9d2e27d94
#5 [internal] load build context
#6 [2/2] COPY . /usr/share/nginx/html/
#7 naming to docker.io/library/cafe-site:1.0 done
```

Each `#N` is one step of the build (`grep` keeps only the step titles here; the full output also shows each step's
progress). `[1/2]` and `[2/2]` are the Dockerfile's `FROM` and `COPY`; `EXPOSE` and `CMD` only add metadata. Run the
image and open the site:

<!-- test: contains=started -->
```bash
docker run -d --name cafe-site -p 8080:80 cafe-site:1.0 > /dev/null && echo "cafe-site started"
```

<!-- test: retry=10; contains=Welcome to the cafe; output -->
```bash
curl -s http://localhost:8080 | grep '<h1>'
```

```text
  <h1>Welcome to the cafe</h1>
```

Your files, inside an image, served by a container. Open <http://localhost:8080> in a browser to see the page.

## Command breakdown

| Command / part | Meaning |
|---|---|
| `docker build -t NAME:TAG .` | build the Dockerfile in `.`, using `.` as the build context |
| `-f path/Dockerfile` | use a Dockerfile with another name or location |
| `# …` | a comment line |
| `INSTRUCTION arguments` | one instruction per line; instructions are written in capitals by convention |
| `docker run -d -p 8080:80` | run in the background, port 8080 on your computer → port 80 in the container (lesson 012) |

## Hands-on lab

**Instructions.** Change the heading of `index.html` to "Welcome to the cafe, version 1.1", build `cafe-site:1.1`,
and run it as `cafe-site-v11` on port 8081.

**Expected result.** `curl http://localhost:8081` shows the new heading; port 8080 still shows the old one.

**Verification.**

<!-- test: contains=lab ready -->
```bash
cd ~/docker-practice/lesson-022
sed -i.bak 's|Welcome to the cafe|Welcome to the cafe, version 1.1|' index.html && rm index.html.bak
docker build -q -t cafe-site:1.1 . > /dev/null
docker run -d --name cafe-site-v11 -p 8081:80 cafe-site:1.1 > /dev/null && echo "lab ready"
```

<!-- test: retry=10; contains=version 1.1 -->
```bash
curl -s http://localhost:8081 | grep '<h1>'
curl -s http://localhost:8080 | grep '<h1>'
```

The running container of 1.0 did not change: an image is fixed once built.

## Break it

A typing error in an instruction:

<!-- test: contains=unknown instruction; output -->
```bash
printf 'FROM nginx:1.30-alpine\nCOPPY . /usr/share/nginx/html/\n' > Dockerfile.broken
docker build -f Dockerfile.broken -t cafe-site:broken . 2>&1 | grep -E '>>>|ERROR'
```

```text
   2 | >>> COPPY . /usr/share/nginx/html/
ERROR: failed to build: failed to solve: dockerfile parse error on line 2: unknown instruction: COPPY (did you mean COPY?)
```

## Troubleshoot it

`dockerfile parse error on line 2: unknown instruction: COPPY`: the build stopped before running anything, while
**reading** the Dockerfile. The `>>>` marks the line, and Docker even suggests the fix. Read build errors from the
`ERROR:` line upwards: the line number, then the failing instruction. No image was created:

<!-- test: contains=no image -->
```bash
docker image inspect cafe-site:broken > /dev/null 2>&1 || echo "no image cafe-site:broken"
```

## Fix it

<!-- test: contains=cafe-site:fixed -->
```bash
sed -i.bak 's/^COPPY/COPY/' Dockerfile.broken && rm Dockerfile.broken.bak
docker build -q -f Dockerfile.broken -t cafe-site:fixed . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-site
```

## Practice challenge

Write a Dockerfile, `Dockerfile.hello`, for an image that only prints `Hello from my first image` when it runs, based
on `alpine:3.23`. Build it as `hello-image:1.0` and run it.

<details>
<summary>Solution</summary>

<!-- test: contains=Hello from my first image; output -->
```bash
cd ~/docker-practice/lesson-022
printf 'FROM alpine:3.23\nCMD ["echo", "Hello from my first image"]\n' > Dockerfile.hello
docker build -q -f Dockerfile.hello -t hello-image:1.0 . > /dev/null
docker run --rm hello-image:1.0
```

```text
Hello from my first image
```

Two instructions are enough: the base image and the command. No `COPY` is needed because the image adds no files.

</details>

## Real-world example

Every service repository of a team has a `Dockerfile` at its root, reviewed in pull requests like the code. CI runs
`docker build` on every commit, so a broken instruction fails the pipeline within seconds, long before a deployment.
The Dockerfile replaces pages of "how to set up the server" documentation with a recipe that is executed, and
therefore always up to date.

## Recap

- A Dockerfile is the recipe of an image: `FROM`, then instructions that add files, run commands and set metadata.
- `docker build -t NAME:TAG .` builds it; `.` is the build context.
- Parse errors name the line and the instruction; nothing is built until the file parses.
- An image is fixed once built: a change means a new build and a new tag.

## Cleanup

<!-- test -->
```bash
docker rm -f cafe-site cafe-site-v11 > /dev/null
docker image rm -f cafe-site:1.0 cafe-site:1.1 cafe-site:fixed hello-image:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-022
```

Next: [Lesson 023 · FROM: choosing a base image](../023-from/README.md)
