<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 083 · Secrets in images · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

"But the credentials file is deleted": the Dockerfile copies it, uses it and removes it. Indeed, it is not in the
running container:

```bash
docker run --rm cafe-secrets:leaky cat /tmp/credentials.txt 2>&1 || true
```

```text
cat: can't open '/tmp/credentials.txt': No such file or directory
```

## Troubleshoot it

A container shows only the **top** of the layer stack; deleting a file in a later layer only hides it. The layer that
`COPY` created is still in the image, and every copy of it. Export the image and read the file from that layer:

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

```bash
docker build -q --secret id=api_token,src=fixed/api_token.txt -t cafe-secrets:fixed fixed > /dev/null
docker image ls cafe-secrets --format '{{.Repository}}:{{.Tag}}'
```

Verify that the token is nowhere in the image: not in the history, the configuration, or any layer:

```bash
docker history --no-trunc cafe-secrets:fixed | grep -q example-token || echo "no token in history"
docker image inspect cafe-secrets:fixed | grep -q example-token || echo "no token in configuration"
rm -rf saved && mkdir saved
docker save cafe-secrets:fixed -o saved/image.tar && tar -xf saved/image.tar -C saved
found=no; for layer in saved/blobs/sha256/*; do tar -xOf "$layer" 2>/dev/null | grep -q example-token && found=yes; done
[ "$found" = no ] && echo "no token in layers"
```
