<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 034 · Dockerfile best practices · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Ask Docker's checker about the first version:

```bash
docker build --check -f Dockerfile.before . 2>&1
```

```text
...
WARNING: JSONArgsRecommended - https://docs.docker.com/go/dockerfile/rule/json-args-recommended/
JSON arguments recommended for CMD to prevent unintended behavior related to OS signals
Dockerfile.before:7
--------------------
   5 |     RUN npm install
   6 |     EXPOSE 3000
   7 | >>> CMD node server.js
   8 |     
--------------------
```

## Troubleshoot it

`--check` runs Docker's build checks (rules such as `JSONArgsRecommended`, `SecretsUsedInArgOrEnv`, `FromAsCasing`,
`UndefinedVar`) without building, and exits with status 1 when it finds something, so it can fail a CI job. Each
warning names the rule, links to its documentation, and marks the line. It cannot see everything: running as root and
copying the whole folder are not "errors", so a review against the practices above is still needed. Here it found the
shell-form `CMD`: `node` is started through `/bin/sh -c`. Some shells replace themselves with a single command,
others stay in between and do not pass `docker stop`'s signal on; with the exec form there is no doubt.

```bash
docker image inspect --format '{{json .Config.Cmd}}' cafe-api:before
```

```text
["/bin/sh","-c","node server.js"]
```

## Fix it

The improved version passes the checks:

```bash
docker build --check -f Dockerfile.after . 2>&1 | tail -1
```
