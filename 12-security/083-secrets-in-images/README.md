# Lesson 083 · Secrets in images

> Level 13 · Container security · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

Anyone who can pull an image can read **everything** in it: every layer, the build history and the metadata. A secret
that reached the image in any of these ways is leaked, even if a later step deletes it:

- `ARG TOKEN` used in a `RUN` step → stored in the **history**,
- `ENV PASSWORD=…` → stored in the image **configuration**,
- `COPY credentials …` then `RUN rm …` → still in the **layer** that the `COPY` created.

The fix: **build secrets** (`RUN --mount=type=secret`) for secrets needed during the build, and **runtime**
configuration for secrets the application needs (lessons 060, 061).

## Visual

```text
  Leaky Dockerfile                                     Where the secret ends up (forever, in every copy)

  ARG API_TOKEN                     ─────────────────▶  docker history   "RUN |1 API_TOKEN=example-token…"
  ENV DB_PASSWORD=…                 ─────────────────▶  docker inspect   Config.Env
  COPY credentials.txt /tmp/        ─────────────────▶  layer 3          tmp/credentials.txt   ◀── still here
  RUN rm /tmp/credentials.txt       ─────────────────▶  layer 4          "file deleted" marker only

  Fixed Dockerfile
  RUN --mount=type=secret,id=api_token …  ──────────▶  /run/secrets/api_token exists during this step only:
  docker build --secret id=api_token,src=api_token.txt   nothing in layers, history or metadata
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-083 12-security/083-secrets-in-images/examples/leaky 12-security/083-secrets-in-images/examples/fixed
cd ~/docker-practice/lesson-083
ls leaky fixed
```

`leaky/` leaks a token in the three ways above. `fixed/` uses a build secret. All secrets in the course are fake.

## Demonstration

Build the leaky image the way a teammate might, passing the token as a build argument:

<!-- test: contains=cafe-secrets:leaky -->
```bash
docker build -q --build-arg API_TOKEN=example-token-change-me-1234 -t cafe-secrets:leaky leaky > /dev/null
docker image ls cafe-secrets --format '{{.Repository}}:{{.Tag}}'
```

It works. Now read it as anyone with access to the image would. The build history:

<!-- test: contains=API_TOKEN=example-token-change-me-1234; output -->
```bash
docker history --no-trunc --format '{{.CreatedBy}}' cafe-secrets:leaky | grep -i token
```

```text
RUN |1 API_TOKEN=example-token-change-me-1234 /bin/sh -c cat /tmp/credentials.txt > /dev/null && rm /tmp/credentials.txt # buildkit
RUN |1 API_TOKEN=example-token-change-me-1234 /bin/sh -c echo "downloading private packages with token ${API_TOKEN}" > /dev/null # buildkit
ARG API_TOKEN=example-token-change-me-1234
```

The configuration:

<!-- test: contains=DB_PASSWORD=example-password-change-me; output -->
```bash
docker image inspect --format '{{range .Config.Env}}{{println .}}{{end}}' cafe-secrets:leaky
```

```text
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
DB_PASSWORD=example-password-change-me
```

Both leaks need no tools and no access to the build machine: only the image, which is usually pushed to a registry
that many people and systems can pull from.

## Command breakdown

| Command / instruction | What it does |
|---|---|
| `docker history --no-trunc IMG` | the instruction that created every layer, in full |
| `docker image inspect --format '{{.Config.Env}}'` | the environment variables baked into the image |
| `docker save IMG -o FILE.tar` | the image as an archive: every layer as a tar file |
| `RUN --mount=type=secret,id=NAME` | mount a secret at `/run/secrets/NAME` for this one step |
| `docker build --secret id=NAME,src=FILE` | provide that secret from a file on the build machine |

## Hands-on lab

**Instructions.** Find the layer created by `COPY credentials.txt` in the leaky image's history and note its size.

**Expected result.** A layer created by `COPY credentials.txt /tmp/credentials.txt` with a non-zero size; the
following `RUN … rm` layer does not make the image smaller.

**Verification.**

<!-- test: contains=COPY credentials.txt -->
```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' cafe-secrets:leaky | head -4
```

## Break it

"But the credentials file is deleted": the Dockerfile copies it, uses it and removes it. Indeed, it is not in the
running container:

<!-- test: contains=No such file; output -->
```bash
docker run --rm cafe-secrets:leaky cat /tmp/credentials.txt 2>&1 || true
```

```text
cat: can't open '/tmp/credentials.txt': No such file or directory
```

## Troubleshoot it

A container shows only the **top** of the layer stack; deleting a file in a later layer only hides it. The layer that
`COPY` created is still in the image, and every copy of it. Export the image and read the file from that layer:

<!-- test: contains=example-token-change-me-1234; output -->
```bash
mkdir -p saved
docker save cafe-secrets:leaky -o saved/image.tar
tar -xf saved/image.tar -C saved
for layer in saved/blobs/sha256/*; do tar -xOf "$layer" tmp/credentials.txt 2>/dev/null || true; done
```

```text
example-token-change-me-1234
```

That loop is all an attacker needs. Once a secret has been in an image that left your machine, the only fix is to
**revoke and rotate the secret**; rebuilding the image does not remove the copies already pulled.

## Fix it

The fixed Dockerfile mounts the secret only for the step that needs it:

<!-- test: contains=type=secret; output -->
```bash
cat fixed/Dockerfile
```

```text
FROM alpine:3.23
# the secret is mounted only while this RUN step runs: it is never written to a layer, the history or the metadata
RUN --mount=type=secret,id=api_token \
    test -s /run/secrets/api_token && echo "token available during this step only" > /dev/null
# runtime secrets (database passwords) are given when the container starts, never in the image (lesson 061)
CMD ["sh", "-c", "echo app started"]
```

Build it, giving the secret from a file (the file is in `.dockerignore`, so it is not even sent as build context):

<!-- test: contains=cafe-secrets:fixed -->
```bash
docker build -q --secret id=api_token,src=fixed/api_token.txt -t cafe-secrets:fixed fixed > /dev/null
docker image ls cafe-secrets --format '{{.Repository}}:{{.Tag}}'
```

Verify that the token is nowhere in the image: not in the history, the configuration, or any layer:

<!-- test: contains=no token in history; contains=no token in configuration; contains=no token in layers -->
```bash
docker history --no-trunc cafe-secrets:fixed | grep -q example-token || echo "no token in history"
docker image inspect cafe-secrets:fixed | grep -q example-token || echo "no token in configuration"
rm -rf saved && mkdir saved
docker save cafe-secrets:fixed -o saved/image.tar && tar -xf saved/image.tar -C saved
found=no; for layer in saved/blobs/sha256/*; do tar -xOf "$layer" 2>/dev/null | grep -q example-token && found=yes; done
[ "$found" = no ] && echo "no token in layers"
```

## Practice challenge

The application needs `DB_PASSWORD` at run time. Remove it from the image entirely and provide it when the container
starts, from a file, so the password is not in the image and not in your shell history. Prove that the image has no
`DB_PASSWORD`, but the container does.

<details>
<summary>Solution</summary>

<!-- test: contains=image: no DB_PASSWORD; contains=container: DB_PASSWORD=example-password-change-me; output -->
```bash
printf 'DB_PASSWORD=example-password-change-me\n' > db.env
docker image inspect --format '{{.Config.Env}}' cafe-secrets:fixed | grep -q DB_PASSWORD || echo "image: no DB_PASSWORD"
echo "container: $(docker run --rm --env-file db.env cafe-secrets:fixed sh -c 'env | grep DB_PASSWORD')"
```

```text
image: no DB_PASSWORD
container: DB_PASSWORD=example-password-change-me
```

`--env-file` (lesson 060) keeps the value out of the image and the command line. Note that environment variables are
still visible with `docker inspect` on the **container**: for real secrets, prefer secret files mounted at run time
(Compose and Kubernetes secrets, lesson 061).

</details>

## Real-world example

Private package registries (npm, PyPI, Maven) need a token during `npm ci` or `pip install`. Teams pass it with
`RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci` and `docker build --secret id=npmrc,src=$HOME/.npmrc`; in
GitHub Actions, the `docker/build-push-action` takes the same secrets from the repository's encrypted secrets. Secret
scanners (for example in the registry or CI) check pushed images for keys and tokens, because leaks like this one are
common.

## Recap

- Anything in an image's layers, history or configuration is readable by everyone who can pull it.
- `ARG` values used in `RUN` appear in `docker history`; `ENV` values appear in `docker inspect`.
- Deleting a file in a later layer does not remove it from the earlier layer.
- Build-time secrets: `RUN --mount=type=secret` + `docker build --secret`. Run-time secrets: given at start, never in
  the image. A leaked secret must be rotated.

## Cleanup

<!-- test -->
```bash
docker image rm -f cafe-secrets:leaky cafe-secrets:fixed > /dev/null
cd ~ && rm -rf ~/docker-practice/lesson-083
```

Next: [Lesson 084 · Read-only file systems](../084-read-only-filesystems/README.md)
