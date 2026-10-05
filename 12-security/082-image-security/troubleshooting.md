<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 082 · Image security: trusted, minimal, pinned, scanned · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Copy a digest from a chat message and lose half of it on the way:

```bash
docker run --rm alpine@sha256:85fe1e81d6758c208f3e1eed 2>&1
```

```text
docker: invalid reference format

Run 'docker run --help' for more information
```

## Troubleshoot it

`invalid reference format`: Docker did not even contact a registry. A digest reference must be exactly
`name@sha256:` followed by **64** hexadecimal characters. Count them:

```bash
printf '%s' 85fe1e81d6758c208f3e1eed | wc -c
```

```text
24
```

24 characters, so the reference is truncated. A digest is never typed by hand: copy it from the source of truth.

## Fix it

Read the digest from the image (or from the registry, `docker buildx imagetools inspect IMAGE`) and use it unchanged:

```bash
digest=$(docker image inspect --format '{{index .RepoDigests 0}}' alpine:3.23)
echo "${digest#*sha256:}" | tr -d '\n' | wc -c
docker run --rm "$digest" true && echo "digest reference works"
```
