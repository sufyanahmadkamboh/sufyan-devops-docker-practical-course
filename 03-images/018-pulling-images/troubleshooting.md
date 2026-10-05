<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 018 · Pulling images · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Pull an image name that does not exist:

```bash
docker image pull cafe-menu-api:1.0 2>&1
```

```text
Error response from daemon: pull access denied for cafe-menu-api, repository does not exist or may require 'docker login'
```

## Troubleshoot it

`pull access denied … repository does not exist or may require 'docker login'`: Docker expanded the name to
`docker.io/library/cafe-menu-api:1.0`, and Docker Hub refused it. The registry deliberately gives the same answer for
"does not exist" and "exists but is private", so you check both. (An engine that pulls through a registry mirror, as CI
machines often do, reports the same problem as `docker.io/library/cafe-menu-api:1.0: not found`.)

1. **The name.** Is it spelled correctly, with the right namespace? Your team's image is probably
   `docker.io/yourteam/cafe-menu-api` or on another registry (`ghcr.io/yourteam/cafe-menu-api`), not an official
   `library/` image.
2. **The tag.** A wrong tag on an existing repository gives `manifest unknown` / `not found` instead.
3. **Access.** A private repository needs `docker login REGISTRY` first (lesson 076).
4. **The rate limit.** `429 Too Many Requests` is not about the name at all: wait, log in, or use a mirror.

Check what the name expands to and whether such an image exists locally:

```bash
docker image inspect docker.io/library/cafe-menu-api:1.0 > /dev/null 2>&1 || echo "no local image docker.io/library/cafe-menu-api:1.0"
```

## Fix it

Use the full, correct name. A safe pattern for scripts pulls only when the image is missing, so it does not spend a
registry request (or fail on a rate limit) when the image is already there:

```bash
docker image inspect busybox:1.37 > /dev/null 2>&1 || docker image pull busybox:1.37
echo "busybox ready: $(docker image inspect --format '{{.Id}}' busybox:1.37 | cut -c1-19)"
```
