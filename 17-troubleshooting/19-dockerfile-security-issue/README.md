# Troubleshooting problem 19 · Dockerfile security issue: a secret in the image

> ⏱ 20 minutes · run every command from the course folder · related lessons: 031, 061, 083

## Problem

The pricing image needs an access token to download a private price feed during the build. The token was passed with
`--build-arg`, "so it is not in the Dockerfile". The image was pushed to a shared registry. A colleague reads the
token from the image in one command.

## Symptoms

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh trouble-19 17-troubleshooting/19-dockerfile-security-issue/examples
cd ~/docker-practice/trouble-19
docker build -q -f broken.Dockerfile --build-arg API_TOKEN="$(cat api-token.txt)" -t pricing-feed:broken . > /dev/null
docker run --rm pricing-feed:broken
```

Anyone who can pull the image:

<!-- test: contains=example-token-not-real; output -->
```bash
docker history --no-trunc --format '{{.CreatedBy}}' pricing-feed:broken | grep -o 'API_TOKEN=[^ ]*'
```

```text
API_TOKEN=example-token-not-real
API_TOKEN=example-token-not-real
```

## Investigation

**1. Where is it stored?** The build history records the values of the build arguments a `RUN` step used:

<!-- test: contains=API_TOKEN; output -->
```bash
docker history --no-trunc --format '{{.CreatedBy}}' pricing-feed:broken | grep RUN | cut -c1-110
```

```text
RUN |1 API_TOKEN=example-token-not-real /bin/sh -c test -n "$API_TOKEN" && echo "price feed downloaded" > /fee
```

**2. Is it also in the configuration?** `ARG` values are not in the environment of the running container, but an
`ENV` would be, and `docker inspect` shows those to anyone:

<!-- test: absent=example-token-not-real; output -->
```bash
docker image inspect --format '{{json .Config.Env}}' pricing-feed:broken
```

```text
["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"]
```

**3. Search the whole image like an attacker would:** the metadata travels with the image to every registry and
every machine that pulls it:

<!-- test: contains=found in the image metadata; output -->
```bash
docker image save -o broken.tar pricing-feed:broken
grep -a -q example-token-not-real broken.tar && echo "token found in the image metadata"
```

```text
token found in the image metadata
```

## Commands

| Command | What it tells you |
|---|---|
| `docker history --no-trunc IMAGE` | every instruction, including build-argument values used by `RUN` |
| `docker image inspect --format '{{json .Config.Env}}' IMAGE` | variables baked in with `ENV` |
| `docker image save -o FILE IMAGE` + `grep -a TEXT FILE` | whether a string is anywhere in the image (layers and metadata) |
| `docker run --rm IMAGE find / -name '*.pem' …` | key or credential files left in a layer |

## Output interpretation

| How the secret was passed | Where it ends up |
|---|---|
| `ARG` + `--build-arg` | the build history of the image (`docker history`) |
| `ENV` | the image configuration and every container's environment |
| `COPY secret.txt` + `RUN rm secret.txt` | still in the earlier layer: deleting it in a later layer hides it, nothing more |
| `RUN --mount=type=secret` | nowhere: mounted for that step only |

Images are made to be copied: registries, CI caches, every server. Whatever is in an image's layers or metadata
must be treated as public within that audience.

## Root cause

The token was passed as a build argument and used by a `RUN` step, so BuildKit recorded it in the image history.

## Fix

**First, revoke the token**: it was published with the image, and removing the image does not un-publish it. Then
pass the new token as a **build secret** (lesson 083):

<!-- test: contains=--mount=type=secret; output -->
```bash
grep -n 'RUN\|mount' fixed.Dockerfile
```

```text
2:# The token is mounted for this one RUN step only (/run/secrets/api_token): it is never written to a layer,
4:RUN --mount=type=secret,id=api_token \
```

<!-- test: contains=price feed downloaded; output -->
```bash
docker build -q -f fixed.Dockerfile --secret id=api_token,src=api-token.txt -t pricing-feed:fixed . > /dev/null
docker run --rm pricing-feed:fixed
```

```text
price feed downloaded
```

## Verification

<!-- test: contains=token not found; output -->
```bash
docker history --no-trunc --format '{{.CreatedBy}}' pricing-feed:fixed | grep -c example-token-not-real || true
docker image save -o fixed.tar pricing-feed:fixed
grep -a -q example-token-not-real fixed.tar || echo "token not found in the image"
```

```text
0
token not found in the image
```

## Prevention

- Never pass secrets with `ARG`, `ENV` or `COPY`. Build time: `RUN --mount=type=secret` (or `type=ssh` for Git).
  Run time: environment from a secret store, Docker/Compose secrets, Kubernetes Secrets (lesson 061).
- Scan images for secrets in CI and review `docker history --no-trunc` of release images (lesson 137).
- Keep secret files out of the build context with `.dockerignore` (`*.pem`, `.env`, `*token*`).
- If a secret was ever in an image: rotate it first, then rebuild and delete the old tags.

## Cleanup

<!-- test -->
```bash
docker image rm pricing-feed:broken pricing-feed:fixed > /dev/null
rm -rf ~/docker-practice/trouble-19
```

Next: [Problem 20 · Running as root](../20-running-as-root/README.md)
