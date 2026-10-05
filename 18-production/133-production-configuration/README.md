# Lesson 133 · Production configuration

> Level 19 · Production · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

**Build once, configure per environment.** The image that passed the tests in staging must be the same bytes that run
in production; only its configuration changes. Configuration therefore comes from outside the image, in three forms:
**environment variables** for simple values, **configuration files mounted read-only** for structured settings, and
**secret files** (never environment variables, never the image) for passwords and keys.

## Visual

```text
                         one image  node-api:1.0  (sha256:… identical everywhere)
                                          │
              ┌───────────────────────────┼───────────────────────────┐
              ▼                           ▼                           ▼
          development                  staging                    production
   -e GREETING="Hello dev"       -e GREETING=…                 -e GREETING=…
                                 -v staging.conf:…:ro          -v prod.conf:/etc/…:ro
                                 -v secrets/key:/run/…:ro      -v secrets/key:/run/secrets/key:ro

 precedence: image defaults (ENV)  <  environment variables  <  mounted files
 secrets:    files under /run/secrets, read-only, never in `docker inspect`, never in the image
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-133 examples/node-api
cp 18-production/130-production-dockerfile/examples/final/Dockerfile 18-production/130-production-dockerfile/examples/final/.dockerignore ~/docker-practice/lesson-133/
cp 18-production/133-production-configuration/examples/default.conf ~/docker-practice/lesson-133/
cd ~/docker-practice/lesson-133
docker build -q -t node-api:1.0 . > /dev/null
```

The image is the production image of lesson 130; `default.conf` is an Nginx configuration for one environment.

## Demonstration

**1. One image, two environments.** Start the same image twice, with different environment variables:

<!-- test: contains=staging -->
```bash
docker run -d --name api-staging -p 8081:3000 -e GREETING="Hello from staging" -e APP_VERSION=1.0 node-api:1.0 > /dev/null
docker run -d --name api-production -p 8082:3000 -e GREETING="Hello from production" -e APP_VERSION=1.0 node-api:1.0 > /dev/null
docker ps --filter name=api- --format '{{.Names}}'
```

<!-- test: retry=10; contains=Hello from production; output -->
```bash
curl -s http://localhost:8081/ && echo
curl -s http://localhost:8082/ && echo
docker inspect api-staging api-production --format '{{.Name}} {{.Image}}'
```

```text
{"message":"Hello from staging","hostname":"311b58c10c42","version":"1.0"}
{"message":"Hello from production","hostname":"bfc59d284d75","version":"1.0"}
/api-staging sha256:7cafbe1c673bc3feb5586f7967810dffada071fa912ec8c7994d1e4bef36d211
/api-production sha256:7cafbe1c673bc3feb5586f7967810dffada071fa912ec8c7994d1e4bef36d211
```

Different behavior, one image ID: what was tested in staging is exactly what runs in production.

**2. A configuration file, mounted read-only.** Nginx reads its site configuration from
`/etc/nginx/conf.d/default.conf`. Mount the environment's file there:

<!-- test: contains=nginx -->
```bash
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
docker ps --filter name=web --format '{{.Names}} {{.Image}}'
```

<!-- test: retry=10; contains=X-Environment: production; output -->
```bash
curl -sI http://localhost:8080/ | grep -i x-environment
curl -s http://localhost:8080/health
```

```text
X-Environment: production
ok
```

**3. A secret, as a file.** An environment variable is visible to anyone who can run `docker inspect`, and is
inherited by every child process. A secret file is not:

<!-- test: contains=API_KEY=example; output -->
```bash
mkdir -p secrets && printf 'example-api-key-change-me' > secrets/api_key
docker run -d --name env-secret -e API_KEY=example-api-key-change-me alpine:3.23 sleep 300 > /dev/null
docker run -d --name file-secret -v "$(pwd)/secrets/api_key:/run/secrets/api_key:ro" alpine:3.23 sleep 300 > /dev/null
docker inspect env-secret --format '{{range .Config.Env}}{{println .}}{{end}}' | grep API_KEY
docker inspect file-secret --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -c API_KEY || true
docker exec file-secret cat /run/secrets/api_key && echo
```

```text
API_KEY=example-api-key-change-me
0
example-api-key-change-me
```

The application reads `/run/secrets/api_key` at startup; the value never appears in the container's configuration.
(Compose and Kubernetes provide secrets exactly like this, as files: lessons 061 and 140.)

## Command breakdown

| Option | What it does |
|---|---|
| `-e NAME=value` | one environment variable (lesson 059) |
| `-v "$(pwd)/file:/path/in/container:ro"` | mount one file, read-only (`:ro`) |
| `/run/secrets/NAME` | the conventional place for secret files (Compose and Swarm use it) |
| `docker inspect --format '{{.Config.Env}}'` | every environment variable of a container, readable by any Docker user |
| `curl -sI` | request only the response headers |

## Hands-on lab

**Instructions.** Start a third environment, `api-dev`, on port 8083, with the greeting `Hello from dev` and version
`dev`, from the same image. Verify its answer and that its image ID matches `api-production`.

**Expected result.** The new greeting, and the two image IDs are identical.

**Verification.**

<!-- test: retry=10; contains=same image -->
```bash
docker run -d --name api-dev -p 8083:3000 -e GREETING="Hello from dev" -e APP_VERSION=dev node-api:1.0 > /dev/null
sleep 1
curl -s http://localhost:8083/ && echo
[ "$(docker inspect api-dev --format '{{.Image}}')" = "$(docker inspect api-production --format '{{.Image}}')" ] && echo "same image"
```

## Break it

A new colleague deploys the web server for another environment and mounts the configuration file to a slightly wrong
path:

<!-- test: retry=10; contains=Welcome to nginx; output -->
```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<title>"
curl -sI http://localhost:8080/ | grep -ci x-environment || true
```

```text
<title>Welcome to nginx!</title>
0
```

No error anywhere: the container is running, and it serves the Nginx welcome page without the `X-Environment` header.

## Troubleshoot it

A configuration that is silently ignored is the hardest kind of mistake. Ask both sides: where did Docker mount the
file, and which configuration is Nginx actually using?

<!-- test: contains=/etc/nginx/default.conf; output -->
```bash
docker inspect web --format '{{range .Mounts}}mounted at {{.Destination}} (writable: {{.RW}}){{println}}{{end}}'
docker exec web nginx -T 2>/dev/null | grep "configuration file"
```

```text
mounted at /etc/nginx/default.conf (writable: false)

# configuration file /etc/nginx/nginx.conf:
# configuration file /etc/nginx/mime.types:
# configuration file /etc/nginx/conf.d/default.conf:
```

The file was mounted to `/etc/nginx/default.conf`, but Nginx only loads `/etc/nginx/nginx.conf` and the files it
includes from `/etc/nginx/conf.d/`. `nginx -T` prints the complete configuration Nginx has loaded, with the name of
every file: ours is not among them.

## Fix it

Mount the file to the path the application reads, and verify the loaded configuration, not just the running
container:

<!-- test: retry=10; contains=X-Environment: production -->
```bash
docker rm -f web > /dev/null
docker run -d --name web -p 8080:80 -v "$(pwd)/default.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 1
docker exec web nginx -T 2>/dev/null | grep "configuration file /etc/nginx/conf.d/default.conf"
curl -sI http://localhost:8080/ | grep -i x-environment
```

## Practice challenge

The configuration is mounted read-only. Prove it: try to change the file from inside the container, and show the
error.

<details>
<summary>Solution</summary>

<!-- test: contains=Read-only file system; output -->
```bash
docker exec web sh -c 'echo "# changed" >> /etc/nginx/conf.d/default.conf' 2>&1 || true
```

```text
sh: can't create /etc/nginx/conf.d/default.conf: Read-only file system
```

`:ro` makes the mount read-only inside the container: neither the application nor an attacker who gets into the
container can change its configuration. Changing it means changing the file on the host (or in Git) and restarting
the container.

</details>

## Real-world example

A team builds one image per commit. CI deploys that image to staging with staging's environment variables and its
mounted configuration; after the tests pass there, the same image digest goes to production with production's values.
Database passwords and API keys come from a secret store (Kubernetes Secrets, AWS Secrets Manager, Vault) and arrive
in the container as files. Nobody builds a "production image", so nothing untested ever reaches production.

## Recap

- Build once, configure per environment: the image never contains environment-specific values.
- Environment variables for simple settings; read-only mounted files for structured configuration.
- Secrets as files under `/run/secrets`, not as environment variables (visible in `docker inspect`) and never in the
  image.
- Verify the configuration the application actually loaded (`nginx -T`, a config endpoint), not just that it runs.

## Cleanup

<!-- test -->
```bash
docker rm -f api-staging api-production api-dev web env-secret file-secret > /dev/null
docker image rm -f node-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-133
```

Next: [Lesson 134 · Security review](../134-security-review/README.md)
