<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 079 · GitHub Container Registry · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write the image name a workflow should use for a repository owned by `Cafe-Team` (capital letters) and the Git tag
`v2.3.0`, the way `docker-publish.yml` computes it, and check that Docker accepts it.

## Solution

```bash
GITHUB_REPOSITORY_OWNER=Cafe-Team GITHUB_REF_NAME=v2.3.0 bash -c '
  image=ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/cafe-api:${GITHUB_REF_NAME#v}
  echo "$image"
  docker tag ghcr.io/cafe-team-example/cafe-api:1.0 "$image" && echo "valid name"
  docker image rm "$image" > /dev/null'
```

```text
ghcr.io/cafe-team/cafe-api:2.3.0
valid name
```

`${VAR,,}` lowercases, `${VAR#v}` removes the leading `v`: `v2.3.0` becomes the tag `2.3.0`. (`${VAR,,}` needs bash 4
or newer: GitHub's runners, Linux and Git Bash have it; macOS's built-in bash 3.2 does not, use
`echo "$VAR" | tr '[:upper:]' '[:lower:]'` there.)
