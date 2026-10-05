<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 080 · The attack surface of a container · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Find out whether `ubuntu:24.04`, `alpine:3.23` and the distroless image contain a shell, a package manager and `wget`
or `curl`. Use `docker run --rm --entrypoint …` or `ls` in images that have a shell; for the distroless image, explain
why you cannot look inside it the same way.

## Solution

```bash
for image in ubuntu:24.04 alpine:3.23; do
  echo "$image: $(docker run --rm "$image" sh -c 'for t in sh bash apt-get apk wget curl; do command -v $t > /dev/null && printf "%s " $t; done')"
done
```

```text
ubuntu:24.04: sh bash apt-get 
alpine:3.23: sh apk wget 
```

The distroless image has no shell, so there is nothing to run `command -v` with: that is the point. You inspect it from
the outside instead, for example by listing its files with `docker export` (lesson 082) or its layers with
`docker history`.
