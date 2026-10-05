<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 007 · Images vs containers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Turn the `red` container into an image of its own with `docker commit` (it saves a container's writable layer as a new
image; lesson 022 shows the right way to build images), start a container from it, and then try to delete the image:

```bash
docker commit red lesson-007:red > /dev/null
docker create --name from-red lesson-007:red cat /data.txt > /dev/null
docker image rm lesson-007:red
```

```text
Error response from daemon: conflict: unable to delete lesson-007:red (must be forced) - container df32e98cefb6 is using its referenced image 40b46fbef5bd
```

## Troubleshoot it

`conflict: unable to delete … container … is using its referenced image`: a container is built **on top of** its
image's layers. Even a stopped container needs them, so Docker refuses to delete an image while any container, running
or not, was created from it. Find the containers that use it:

```bash
docker ps -a --filter ancestor=lesson-007:red --format '{{.Names}}: {{.Status}}'
```

```text
from-red: Created
```

## Fix it

Remove the containers first, then the image:

```bash
docker rm from-red > /dev/null
docker image rm lesson-007:red
```

`docker image rm -f` would remove the tag anyway, but it leaves the containers pointing at an image without a name.
Remove the containers first.
