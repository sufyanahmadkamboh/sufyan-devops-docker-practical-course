<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 019 · Listing and removing images · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Start a container from `cafe-site:1.1`, stop it, and then try to remove the image:

```bash
docker run -d --name cafe-site cafe-site:1.1 > /dev/null
docker stop cafe-site > /dev/null
docker image rm cafe-site:1.1
```

```text
Error response from daemon: conflict: unable to delete cafe-site:1.1 (must be forced) - container b16c0e650cea is using its referenced image 6a22e6401e50
```

## Troubleshoot it

`conflict: unable to delete … container 3c9d1b2f8a4e is using its referenced image`: a container needs its image's
layers, even when it is **stopped** (it can be started again). Docker refuses to delete them. Find the containers that
use the image, running or not:

```bash
docker container ls -a --filter ancestor=cafe-site:1.1 --format '{{.Names}}  {{.Status}}'
```

```text
cafe-site  Exited (0) Less than a second ago
```

## Fix it

Remove the container first (if you no longer need it), then the image:

```bash
docker rm cafe-site
docker image rm cafe-site:1.1
```

`docker image rm -f` would remove the *name* anyway, but the stopped container keeps the image's data on disk as an
unnamed image: `-f` hides the problem instead of solving it.
