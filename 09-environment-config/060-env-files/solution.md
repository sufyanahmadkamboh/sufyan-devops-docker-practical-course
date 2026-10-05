<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 060 · Environment files · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

An env file line can be just a variable name. Use that to pass `RELEASE` from your shell through the file, without
writing its value into the file.

## Solution

```bash
printf 'RELEASE\n' > release.env
export RELEASE=2026.10
docker run --rm --env-file release.env alpine:3.23 sh -c 'echo "release $RELEASE"'
```

```text
release 2026.10
```

The file lists **which** variables the container gets; the values come from the environment of whoever runs
`docker`, such as a CI job. That keeps values that change per run (or secrets) out of the file.
