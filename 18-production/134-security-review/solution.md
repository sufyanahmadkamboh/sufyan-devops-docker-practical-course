<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 134 · Security review · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Finding 1 says production should pin the base image by **digest**, which never moves. Find the digest of your
`node:24-alpine` image and print the `FROM` line that pins it.

## Solution

```bash
digest=$(docker image inspect node:24-alpine --format '{{range .RepoDigests}}{{println .}}{{end}}' | head -1 | cut -d@ -f2)
echo "FROM node:24-alpine@$digest"
```

```text
FROM node:24-alpine@sha256:ebfe2f90462722a7a4de65e91990e97fe0d401c70e0e762c5b53302f905ec1c1
```

With both, the tag tells people which version it is and the digest guarantees the exact bytes. Tools such as
Dependabot or Renovate update the digest with a reviewed pull request when a new patch release appears.
