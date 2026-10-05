<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 136 · Build and push with GitHub Actions · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A new team member builds the image as `node-api:main` (no registry in the name) and pushes it:

```bash
cd ~/docker-practice/lesson-136
docker tag localhost:5000/node-api:main node-api:main
docker push node-api:main 2>&1 | grep -v Waiting
test "${PIPESTATUS[0]}" -eq 0
```

```text
The push refers to repository [docker.io/library/node-api]
push access denied, repository does not exist or may require authorization: server message: insufficient_scope: authorization failed
```

(`grep -v Waiting` only hides the progress lines of the layers.)

## Troubleshoot it

The first line of the push output names the repository Docker used: `docker.io/library/node-api`. An image name
without a registry host means Docker Hub, and `library/` is reserved for Docker's official images, so the push is
refused (or, with too many anonymous requests, rate-limited). The name decides the destination (lesson 077):

| Name | Pushed to |
|---|---|
| `node-api:main` | `docker.io/library/node-api` (Docker Hub, official images: refused) |
| `localhost:5000/node-api:main` | the registry on `localhost:5000` |
| `ghcr.io/OWNER/node-api:main` | GitHub Container Registry, owner `OWNER` |

The same mistake in the workflow looks different: pushing to `ghcr.io` without `permissions: packages: write` fails
with `denied: installation not allowed to Create organization package` or `permission_denied: write_package`. Both
mean the same thing: the token may read, not write.

## Fix it

Name the image after its destination, as the metadata step does with `images: ghcr.io/…`:

```bash
cd ~/docker-practice/lesson-136
docker tag node-api:main localhost:5000/node-api:main
docker push -q localhost:5000/node-api:main > /dev/null && echo "pushed localhost:5000/node-api:main"
```
