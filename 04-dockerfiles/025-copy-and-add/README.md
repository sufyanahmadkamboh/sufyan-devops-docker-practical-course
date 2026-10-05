# Lesson 025 · COPY and ADD

> Level 5 · Dockerfiles · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

`COPY` puts files from the **build context** (the folder you pass to `docker build`) into the image. `ADD` does the
same and two extra things: it unpacks local `.tar` archives, and it can download URLs. Because those extras can
surprise you, the rule is simple: use `COPY`, and `ADD` only when you want one of its extras. Neither can reach files
outside the build context.

## Visual

```text
  docker build -t menu .          build context = this folder, sent to the builder
  ┌──────────────────────────┐
  │ menu.csv                 │ ── COPY menu.csv /app/            ──▶ /app/menu.csv
  │ public/index.html        │ ── COPY public/ /app/public/      ──▶ /app/public/index.html  (the folder's contents)
  │ public/styles.css        │
  │ assets.tar               │ ── ADD assets.tar /app/assets/    ──▶ /app/assets/…  (unpacked!)
  └──────────────────────────┘    COPY assets.tar /app/          ──▶ /app/assets.tar (as is)
   ../shared/config.json  ✗  outside the context: COPY cannot see it
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-025 04-dockerfiles/025-copy-and-add/examples
cd ~/docker-practice/lesson-025/menu-service
ls -R
```

`menu-service/` is the build context: the menu and a small `public/` website. `../shared/config.json` sits next to it,
outside.

## Demonstration

Copy a file, and a folder:

<!-- test: contains=/app/public/index.html; output -->
```bash
cat > Dockerfile <<'EOF'
FROM alpine:3.23
WORKDIR /app
COPY menu.csv .
COPY public/ public/
CMD ["find", "/app", "-type", "f"]
EOF
docker build -q -t copy-demo . > /dev/null
docker run --rm copy-demo
```

```text
/app/public/styles.css
/app/public/index.html
/app/menu.csv
```

`COPY public/ public/` copies the **contents** of `public/` into `/app/public/`. A destination ending in `/` is a
directory; `COPY` creates it if needed.

Files are owned by `root` unless you say otherwise. `--chown` sets the owner as the files are copied (users are lesson
033):

<!-- test: contains=nobody; output -->
```bash
printf 'FROM alpine:3.23\nCOPY --chown=nobody:nobody menu.csv /app/\nCMD ["ls", "-l", "/app"]\n' > Dockerfile.chown
docker build -q -f Dockerfile.chown -t copy-demo:chown . > /dev/null
docker run --rm copy-demo:chown
```

```text
total 4
-rwxr-xr-x    1 nobody   nobody          57 Oct  5 16:53 menu.csv
```

Now the difference with `ADD`: give both the same archive.

<!-- test: contains=COPY keeps:; contains=ADD unpacks:; output -->
```bash
tar -cf assets.tar public
printf 'FROM alpine:3.23\nCOPY assets.tar /copy/\nADD assets.tar /add/\n' > Dockerfile.add
docker build -q -f Dockerfile.add -t copy-demo:add . > /dev/null
echo "COPY keeps:  $(docker run --rm copy-demo:add ls /copy)"
echo "ADD unpacks: $(docker run --rm copy-demo:add find /add -type f | tr '\n' ' ')"
```

```text
COPY keeps:  assets.tar
ADD unpacks: /add/public/styles.css /add/public/index.html 
```

`ADD` can also download a URL (`ADD https://example.com/tool.tgz /tmp/`). Remote downloads should be verified, so
modern Dockerfiles add a checksum: `ADD --checksum=sha256:… https://… /tmp/`. For everything else, use `COPY`.

## Command breakdown

| Instruction | Meaning |
|---|---|
| `COPY SRC… DEST` | copy files or folders from the build context |
| `COPY --chown=USER:GROUP` | set the owner of the copied files |
| `COPY --chmod=0755` | set the permissions of the copied files |
| `ADD archive.tar DEST/` | copy and unpack a local tar archive (also `.tar.gz`, `.tar.bz2`, `.tar.xz`) |
| `ADD --checksum=sha256:… URL DEST` | download a file and verify its checksum |
| `COPY --from=STAGE` | copy from another build stage (lesson 087) |

## Hands-on lab

**Instructions.** Build an image whose `/usr/share/nginx/html/` contains the files of `public/`, based on
`nginx:1.30-alpine`, run it on port 8080 and fetch the page.

**Expected result.** `curl` returns the cafe's page.

**Verification.**

<!-- test: contains=started -->
```bash
cd ~/docker-practice/lesson-025/menu-service
printf 'FROM nginx:1.30-alpine\nCOPY public/ /usr/share/nginx/html/\n' > Dockerfile.site
docker build -q -f Dockerfile.site -t copy-demo:site . > /dev/null
docker run -d --name copy-site -p 8080:80 copy-demo:site > /dev/null && echo "started"
```

<!-- test: retry=10; contains=Welcome to the cafe -->
```bash
curl -s http://localhost:8080
```

## Break it

The service also needs the shared configuration file, which lives in the folder next to it:

<!-- test: contains=not found; output -->
```bash
printf 'FROM alpine:3.23\nWORKDIR /app\nCOPY menu.csv .\nCOPY ../shared/config.json .\n' > Dockerfile.config
docker build -f Dockerfile.config -t copy-demo:config . 2>&1 | grep -E '>>>|ERROR'
```

```text
#7 ERROR: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::npbjpnozw376q5hsmeeslrqen: "/shared/config.json": not found
   4 | >>> COPY ../shared/config.json .
ERROR: failed to build: failed to solve: failed to compute cache key: failed to calculate checksum of ref 3cd6gxh0d9ods5a51p5kfp9pm::npbjpnozw376q5hsmeeslrqen: "/shared/config.json": not found
```

## Troubleshoot it

`"/shared/config.json": not found`, although the file exists on your disk. Look at the path in the message: the `..`
is gone. Paths in `COPY` are always **inside** the build context, so `../shared` is cut back to `/shared` within
`menu-service/`, where there is no such folder. Docker sends only the build context to the builder; it cannot read
anything else from your computer (this is a security feature: a Dockerfile from a repository cannot copy your files
from elsewhere). Check what the context contains:

<!-- test: absent=config.json; contains=menu.csv -->
```bash
ls -R .
```

## Fix it

Make the context the folder that contains everything the build needs, and point to the Dockerfile with `-f`:

<!-- test: contains=opening_hours; output -->
```bash
cd ~/docker-practice/lesson-025
printf 'FROM alpine:3.23\nWORKDIR /app\nCOPY menu-service/menu.csv .\nCOPY shared/config.json .\nCMD ["cat", "config.json"]\n' > menu-service/Dockerfile.config
docker build -q -f menu-service/Dockerfile.config -t copy-demo:config . > /dev/null
docker run --rm copy-demo:config
```

```text
{
  "currency": "EUR",
  "opening_hours": "07:00-18:00"
}
```

The context is now `lesson-025/` (the `.`), so both folders are inside it, and the `COPY` paths are relative to it.
The other way is to copy the file into `menu-service/` before building. A large context is slow to send, which
`.dockerignore` solves (lesson 037).

## Practice challenge

Make a `.tar.gz` of the `public/` folder and build an image in which `ADD` unpacks it into `/srv/www/`. Verify that
`/srv/www/public/index.html` exists in the image.

<details>
<summary>Solution</summary>

<!-- test: contains=/srv/www/public/index.html; output -->
```bash
cd ~/docker-practice/lesson-025/menu-service
tar -czf public.tar.gz public
printf 'FROM alpine:3.23\nADD public.tar.gz /srv/www/\n' > Dockerfile.targz
docker build -q -f Dockerfile.targz -t copy-demo:targz . > /dev/null
docker run --rm copy-demo:targz ls /srv/www/public/index.html
```

```text
/srv/www/public/index.html
```

`ADD` recognises compressed archives too. With `COPY`, the file would arrive as `public.tar.gz`, unchanged.

</details>

## Real-world example

A typical Node.js or Python Dockerfile copies in two steps: first only the dependency files (`COPY package*.json ./`,
`COPY requirements.txt .`), install dependencies, then `COPY . .` for the code. Code changes then do not invalidate the
expensive dependency layer (lesson 039). In monorepos, the build context is the repository root and each service's
Dockerfile is selected with `-f services/menu/Dockerfile`, so services can share files from `libs/`.

## Recap

- `COPY` copies from the build context; a folder source copies its contents.
- `--chown` and `--chmod` set ownership and permissions while copying.
- `ADD` also unpacks local archives and downloads URLs: use it only for that.
- Nothing outside the build context can be copied: choose the context (`.`) and the Dockerfile (`-f`) accordingly.

## Cleanup

<!-- test -->
```bash
docker rm -f copy-site > /dev/null
docker image rm -f copy-demo copy-demo:chown copy-demo:add copy-demo:site copy-demo:config copy-demo:targz > /dev/null
rm -rf ~/docker-practice/lesson-025
```

Next: [Lesson 026 · RUN](../026-run/README.md)
