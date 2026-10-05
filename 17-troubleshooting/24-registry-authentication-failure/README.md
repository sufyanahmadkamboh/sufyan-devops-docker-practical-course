# Troubleshooting problem 24 · Registry authentication failure

> ⏱ 20 minutes · run every command from the course folder · related lessons: 076, 078, 079

## Problem

The team's private registry now requires a login. The release script pushes as before and fails with
`no basic auth credentials`; a colleague logs in and gets `401 Unauthorized`.

## Symptoms

Reproduce it with a private registry on your computer (`registry:3` with password authentication, lesson 078). First
the password file, in the `htpasswd` format with a bcrypt hash (the tool comes from Alpine's `apache2-utils` package;
the credentials are examples):

<!-- test: contains=student; output -->
```bash
mkdir -p ~/docker-practice/trouble-24/auth && cd ~/docker-practice/trouble-24
docker run --rm alpine:3.23 sh -c 'apk add -q apache2-utils > /dev/null && htpasswd -Bbn student example-password-change-me' > auth/htpasswd
cut -d: -f1 auth/htpasswd
```

```text
student
```

<!-- test -->
```bash
docker run -d --name registry -p 5000:5000 -v "$(pwd)/auth:/auth" \
  -e REGISTRY_AUTH=htpasswd -e REGISTRY_AUTH_HTPASSWD_REALM="Course registry" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd registry:3 > /dev/null
docker tag busybox:1.37 localhost:5000/team/busybox:1.37
```

The push without logging in:

<!-- test: fail; retry=5; contains=no basic auth credentials; output -->
```bash
docker push -q localhost:5000/team/busybox:1.37 2>&1
```

```text
push access denied, repository does not exist or may require authorization: authorization failed: no basic auth credentials
```

The login with a wrong password:

<!-- test: fail; contains=401 Unauthorized; output -->
```bash
echo "wrong-password" | docker login localhost:5000 -u student --password-stdin 2>&1
```

```text
Error response from daemon: login attempt to http://localhost:5000/v2/ failed with status: 401 Unauthorized
```

## Investigation

**1. What does the registry require?** Ask its API directly (`/v2/` is the registry API's root):

<!-- test: contains=401 Unauthorized; contains=Www-Authenticate; output -->
```bash
curl -si http://localhost:5000/v2/ | grep -iE '^HTTP|^www-authenticate'
```

```text
HTTP/1.1 401 Unauthorized
Www-Authenticate: Basic realm="Course registry"
```

`401` with `WWW-Authenticate: Basic realm="Course registry"`: user name and password required.

**2. Do the credentials work outside Docker?** This separates "wrong credentials" from "Docker does not send them":

<!-- test: contains=200 OK; output -->
```bash
curl -si -u student:example-password-change-me http://localhost:5000/v2/ | grep -i '^HTTP'
```

```text
HTTP/1.1 200 OK
```

**3. What does the registry log?**

<!-- test: contains=authentication; output -->
```bash
docker logs registry 2>&1 | grep -io 'error authenticating user[^"]*\|authentication failure[^"]*\|invalid authorization credential[^"]*' | sort -u | head -3
```

```text
authentication failure
invalid authorization credential
```

**4. Has this Docker client stored credentials for this registry?**

<!-- test: contains=stored login for localhost:5000: no; output -->
```bash
config="${DOCKER_CONFIG:-$HOME/.docker}/config.json"
if grep -q 'localhost:5000' "$config" 2> /dev/null; then echo "stored login for localhost:5000: yes"; else echo "stored login for localhost:5000: no"; fi
```

```text
stored login for localhost:5000: no
```

## Commands

| Command | What it tells you |
|---|---|
| `curl -si https://REGISTRY/v2/` | whether the registry wants authentication (401 + `WWW-Authenticate`) |
| `curl -u USER:PASS https://REGISTRY/v2/` | whether the credentials are right, without Docker |
| `docker login REGISTRY` | stores credentials for **exactly** that host name (and port) |
| `docker logs REGISTRY_CONTAINER` | the server's view of the failed attempts (for your own registry) |

## Output interpretation

| Message | Meaning |
|---|---|
| `no basic auth credentials` | the client has no stored login for this exact registry host |
| `401 Unauthorized` at login | the registry rejected the user name or password |
| `denied: requested access to the resource is denied` | logged in, but no permission for that repository (Docker Hub: wrong namespace) |
| `unauthorized: authentication required` at pull | a private image without a login, or an expired token |

The host name must match: a login to `localhost:5000` is not a login to `127.0.0.1:5000`, and a login to Docker Hub
does not cover `ghcr.io`.

## Root cause

The client had no credentials for `localhost:5000` (no `docker login`), and the colleague's login used a wrong
password.

## Fix

Log in with the right credentials, read from standard input so the password never appears in the shell history or the
process list:

<!-- test: contains=Login Succeeded; output -->
```bash
echo "example-password-change-me" | docker login localhost:5000 -u student --password-stdin 2>&1
```

```text
Login Succeeded
```

The warning (when there is one) says the credentials are stored base64-encoded in `config.json`: configure a
credential helper (Docker Desktop does) on shared machines.

## Verification

<!-- test: contains=team/busybox; output -->
```bash
docker push -q localhost:5000/team/busybox:1.37
curl -s -u student:example-password-change-me http://localhost:5000/v2/_catalog
```

```text
localhost:5000/team/busybox:1.37

 Info -> Not all multiplatform-content is present and only the available single-platform image was pushed
         sha256:bdf57e528e45e4433820e045b29b4597825a1c9e38353532d90a01445013f82e -> sha256:66a6306db78bf2dbf3487f293aa8d6990d8e506fdffab9cc43fe422becf886e4
{"repositories":["team/busybox"]}
```

On Docker Desktop, an `Info` line may add that only the platform present locally was pushed: the local image store
keeps the multi-platform index of `busybox`, but only the layers for your machine. Pull it back from the registry:

<!-- test: contains=localhost:5000/team/busybox:1.37; output -->
```bash
docker image rm localhost:5000/team/busybox:1.37 > /dev/null
docker pull -q localhost:5000/team/busybox:1.37
```

```text
localhost:5000/team/busybox:1.37
```

## Prevention

- In CI, log in with a dedicated token from the secret store, never a personal password: `docker/login-action`, or
  `echo "$TOKEN" | docker login … --password-stdin` (lessons 079, 136).
- Use tokens with the narrowest scope (pull-only for servers, push for CI) and an expiry date.
- Log out on shared machines (`docker logout REGISTRY`) and use a credential helper instead of plain `config.json`.

## Cleanup

<!-- test -->
```bash
docker logout localhost:5000 > /dev/null
docker rm -f registry > /dev/null
docker image rm localhost:5000/team/busybox:1.37 > /dev/null
cd ~ && rm -rf ~/docker-practice/trouble-24
```

Next: [Problem 25 · Image pull failure](../25-image-pull-failure/README.md)
