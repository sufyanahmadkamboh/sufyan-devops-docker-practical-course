# Module 09 assessment · Environment configuration

> Lessons [059](059-environment-variables/README.md)–[061](061-config-vs-secrets/README.md) · ⏱ 30 minutes · try
> every question before opening its answer

## Knowledge check

**1. Why configure containers with environment variables instead of building one image per environment?**

<details><summary>Answer</summary>

So that one tested image runs everywhere: development, staging and production differ only in configuration, never in
the artefact (lesson 059).

</details>

**2. The image sets `ENV LOG_LEVEL=info`, and you run it with `-e LOG_LEVEL=debug`. Which value does the application
see?**

<details><summary>Answer</summary>

`debug`: `-e` overrides the image's default (lesson 059).

</details>

**3. Can you change an environment variable of a running container?**

<details><summary>Answer</summary>

No. The environment is fixed when the container is created; recreate the container with the new value (lesson 059).

</details>

**4. An env file contains `GREETING="Hello"`. What value does `docker run --env-file` pass?**

<details><summary>Answer</summary>

`"Hello"`, with the quotes: `docker run` takes everything after `=` literally (lesson 060).

</details>

**5. Two env files and an `-e` set the same variable. Which one wins?**

<details><summary>Answer</summary>

`-e` wins over the files; between files, the later `--env-file` wins (lesson 060).

</details>

**6. Name three places where a password passed with `-e` becomes visible.**

<details><summary>Answer</summary>

`docker inspect` (anyone with Docker access), the environment of every process in the container (`env`,
`/proc/1/environ`), and anything that dumps the environment: crash reports, debug pages, support tickets (lesson 061).

</details>

**7. What does `POSTGRES_PASSWORD_FILE=/run/secrets/db_password` pass to the container: configuration or a secret?**

<details><summary>Answer</summary>

Configuration: only the path of the secret. The secret itself is the read-only mounted file (lesson 061).

</details>

## Practical task

Start the Node.js API of the course (`examples/node-api`) with an env file `staging.env` that sets
`GREETING=Hello from staging` and `APP_VERSION=2.0.0`, overriding `APP_VERSION` to `2.0.1` on the command line, on
host port 8090.

<details><summary>Solution</summary>

<!-- test: contains=Hello from staging; contains=2.0.1; output; retry=5 -->
```bash
bash scripts/lab.sh assessment-09 examples/node-api > /dev/null
cd ~/docker-practice/assessment-09
printf 'GREETING=Hello from staging\nAPP_VERSION=2.0.0\n' > staging.env
docker run -d --name staging-api -p 8090:3000 --env-file staging.env -e APP_VERSION=2.0.1 \
  -v "$(pwd):/app:ro" -w /app node:24-alpine node server.js > /dev/null
sleep 1
curl -s http://localhost:8090; echo
```

```text
{"message":"Hello from staging","hostname":"e0d391d23e5a","version":"2.0.1"}
```

</details>

## Troubleshooting task

Set up the broken system: a database that a colleague says "keeps crashing".

<!-- test: contains=Exited; retry=5 -->
```bash
mkdir -p ~/docker-practice/assessment-09 && cd ~/docker-practice/assessment-09
printf 'example-assessment-password' > pg_password.txt
docker run -d --name broken-db -v "$(pwd)/pg_password.txt:/run/secrets/pg_password:ro" \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/pg-password postgres:18-alpine > /dev/null
sleep 3
docker ps -a --filter name=broken-db --format '{{.Status}}'
```

Find the cause from the evidence, fix it, and prove the database accepts a password login.

<details><summary>Solution</summary>

The log names the file it could not read; the mount shows the real path. `pg-password` (dash) vs `pg_password`
(underscore):

<!-- test: anyof=pg-password||No such file; contains=/run/secrets/pg_password; output -->
```bash
docker logs broken-db 2>&1 | tail -3
docker inspect broken-db --format '{{range .Mounts}}mounted at {{.Destination}}{{println}}{{end}}'
```

```text
/usr/local/bin/docker-entrypoint.sh: line 21: /run/secrets/pg-password: No such file or directory
mounted at /run/secrets/pg_password
mounted at /var/lib/postgresql
```

<!-- test: contains=login ok; retry=15 -->
```bash
cd ~/docker-practice/assessment-09
docker rm -f broken-db > /dev/null
docker run -d --name broken-db -v "$(pwd)/pg_password.txt:/run/secrets/pg_password:ro" \
  -e POSTGRES_PASSWORD_FILE=/run/secrets/pg_password postgres:18-alpine > /dev/null
sleep 3
docker exec -e PGPASSWORD="$(cat pg_password.txt)" broken-db psql -h 127.0.0.1 -U postgres -tAc "select 'login ok'"
```

</details>

## Real-world scenario

A developer's pull request adds `ENV STRIPE_API_KEY=sk_live_…` to the Dockerfile "so the payments service works in
every environment", and the CI pushes the image to the company registry. What is wrong, and what must happen now?

<details><summary>Model answer</summary>

Three problems. The key is a secret, and `ENV` bakes it into the image: anyone who can pull the image reads it with
`docker image inspect` or `docker history` (lesson 083). It is the same in every environment, so a test system uses
the live key. And it is now in Git history and in the registry. Actions: revoke and rotate the key immediately
(deleting the commit is not enough), remove the `ENV` line, delete the pushed image tags, and pass the key at runtime
as a secret file (`/run/secrets/stripe_api_key`, with the application reading a `*_FILE` variable), different per
environment (lesson 061).

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f staging-api broken-db > /dev/null
rm -rf ~/docker-practice/assessment-09
```
