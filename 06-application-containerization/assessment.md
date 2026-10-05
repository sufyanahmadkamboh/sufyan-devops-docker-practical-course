# Module 06 assessment · Application containerization

> Lessons [040](040-containerize-node/README.md)–[045](045-comparing-stacks/README.md) · ⏱ 45 minutes · try every
> question before opening its answer

## Knowledge check

**1. Why `npm ci` instead of `npm install` in a Dockerfile?**

<details><summary>Answer</summary>

`npm ci` installs exactly the versions in `package-lock.json` and fails without it, so every build installs the same
code. `npm install` may resolve newer versions (lesson 040).

</details>

**2. Why `CMD ["node", "server.js"]` rather than `CMD ["npm", "start"]` or `CMD node server.js`?**

<details><summary>Answer</summary>

With the exec form, `node` itself is PID 1 and receives `SIGTERM` from `docker stop`, so it can shut down cleanly.
`npm` or a shell in between may not forward the signal, and Docker kills the container after the 10 s timeout
(lesson 040).

</details>

**3. What does `PYTHONUNBUFFERED=1` change?**

<details><summary>Answer</summary>

Python writes output immediately instead of buffering it, so log lines appear in `docker logs` when they happen
(lesson 041).

</details>

**4. A Flask app runs in a container, the port is published, but `curl` gets `Empty reply from server`. What is the
most likely cause?**

<details><summary>Answer</summary>

The server listens on `127.0.0.1` inside the container (Flask's development server default). It must listen on
`0.0.0.0`; published traffic arrives on the container's network interface, not its loopback (lesson 041).

</details>

**5. What does `CGO_ENABLED=0` give a Go build, and why does it matter for containers?**

<details><summary>Answer</summary>

A static binary that does not depend on the C library of the image. It runs on any Linux image, including Alpine,
distroless and `scratch` (lessons 042, 089).

</details>

**6. A Java container with `-m 1g` gets a maximum heap of about 256 MB. Why, and how do you change it?**

<details><summary>Answer</summary>

The JVM respects the container limit and uses 25 % of it for the heap by default. Set `-XX:MaxRAMPercentage=75`
(directly or via `JAVA_TOOL_OPTIONS`) (lesson 043).

</details>

**7. Why does a PHP application usually need two containers?**

<details><summary>Answer</summary>

PHP-FPM executes PHP and speaks FastCGI (port 9000); it is not an HTTP server. Nginx receives HTTP, serves static
files, and forwards PHP requests to FPM (lesson 044).

</details>

**8. Nginx exits with `host not found in upstream "php"`. What do you check?**

<details><summary>Answer</summary>

That a container named `php` is running on the same user-defined network as Nginx; Nginx resolves upstream names at
start-up (lesson 044).

</details>

## Practical task

Containerize the course's Go API (`examples/go-api`) as `assess-go:1.0` so that it runs as a non-root user, publish it
on port 8094, and prove both: `/health` answers and the process is not root.

<details><summary>Solution</summary>

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-06 examples/go-api
cat > ~/docker-practice/assessment-06/Dockerfile <<'EOF'
FROM golang:1.26-alpine
WORKDIR /src
COPY go.mod ./
RUN go mod download
COPY main.go ./
RUN CGO_ENABLED=0 go build -o /usr/local/bin/go-api .
USER nobody
EXPOSE 8080
CMD ["go-api"]
EOF
(cd ~/docker-practice/assessment-06 && docker build -q -t assess-go:1.0 . > /dev/null)
docker run -d --name assess-go -p 8094:8080 assess-go:1.0 > /dev/null
```

<!-- test: retry=10; contains="status":"ok"; contains=nobody -->
```bash
curl -s http://localhost:8094/health
docker exec assess-go whoami
```

</details>

## Troubleshooting task

A colleague runs the Node.js API from lesson 040 and reports that it is "broken". Reproduce their command:

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh assessment-06-node examples/node-api
cd ~/docker-practice/assessment-06-node
printf 'FROM node:24-alpine\nWORKDIR /app\nCOPY package.json server.js ./\nUSER node\nCMD ["node", "server.js"]\n' > Dockerfile
docker build -q -t assess-node:1.0 . > /dev/null
docker run -d --name assess-node -p 8095:8080 assess-node:1.0 > /dev/null
sleep 1
```

<!-- test: fail; anyof=Empty reply||Connection reset||Recv failure -->
```bash
curl -sS http://localhost:8095/ 2>&1
```

Find the cause with Docker commands only and fix it without rebuilding the image.

<details><summary>Solution</summary>

The container runs; the application says which port it uses, and Docker says which port is published:

<!-- test: contains=port 3000; contains=8080/tcp -->
```bash
docker logs assess-node
docker port assess-node
```

The application listens on 3000; the mapping sends traffic to 8080, where nothing listens. Either publish the right
container port, or tell the application to listen on 8080 (`-e PORT=8080`):

<!-- test: contains=Hello from Node.js -->
```bash
docker rm -f assess-node > /dev/null
docker run -d --name assess-node -p 8095:3000 assess-node:1.0 > /dev/null
sleep 1
curl -s http://localhost:8095/
```

</details>

## Real-world scenario

Your team is moving five services (Node.js, Python, Go, Java, PHP) to containers. Management asks for "one standard
Dockerfile for everything". What can be standard, and what must differ per stack?

<details><summary>Model answer</summary>

Standard for all: official, pinned base images; dependency manifests copied and installed before the code; a
`.dockerignore`; an unprivileged user; an exec-form start command; configuration through environment variables; labels
and a health check; size and memory measured (lessons 040–045).

Per stack: the build tool (npm, pip, go, Maven/Gradle, Composer), the runtime base (Node.js, Python, distroless for Go,
a JRE, PHP-FPM plus Nginx), the server process (gunicorn/uvicorn for Python, FPM behind Nginx for PHP) and runtime
tuning (JVM heap percentage, worker counts). The practical answer is one template per stack that shares the common
rules, not one Dockerfile.

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f assess-go assess-node > /dev/null 2>&1 || true
docker image rm -f assess-go:1.0 assess-node:1.0 > /dev/null 2>&1 || true
rm -rf ~/docker-practice/assessment-06 ~/docker-practice/assessment-06-node
```
