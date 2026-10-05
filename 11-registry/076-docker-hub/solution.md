<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 076 · Docker Hub · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Show the difference between a tag and a digest: give the `nginx:1.29-alpine` image the tag `cafe/web:stable`, then
"release" `nginx:1.30-alpine` under the same tag. Print which nginx version `cafe/web:stable` runs before and after,
and which one the registry digest of `nginx:1.29-alpine` (noted before the release) runs.

## Solution

```bash
docker tag nginx:1.29-alpine cafe/web:stable
pinned=$(docker image inspect nginx:1.29-alpine --format '{{range .RepoDigests}}{{println .}}{{end}}' | grep '^nginx@')
echo "stable before: $(docker run --rm --entrypoint nginx cafe/web:stable -v 2>&1)"
docker tag nginx:1.30-alpine cafe/web:stable
echo "stable after:  $(docker run --rm --entrypoint nginx cafe/web:stable -v 2>&1)"
echo "digest still runs $(docker run --rm --entrypoint nginx "$pinned" -v 2>&1 | cut -d' ' -f3)"
docker image rm cafe/web:stable > /dev/null
```

```text
stable before: nginx version: nginx/1.29.8
stable after:  nginx version: nginx/1.30.5
digest still runs nginx/1.29.8
```

A tag is a movable pointer, on Docker Hub as locally. (The digest is taken from `nginx@…`, the name it has on Docker
Hub: a digest is only useful together with a repository that holds that content.) Production deployments that must be reproducible pin by digest
(`nginx@sha256:…`), or at least by a full version tag, never by `latest` (lesson 021).
