<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 100 · Metadata and docker inspect · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A script that worked for containers is pointed at an image:

```bash
docker inspect --format '{{.State.Status}}' nginx:1.30-alpine 2>&1
```

```text

template parsing error: template: :1:8: executing "" at <.State.Status>: map has no entry for key "State"
```

## Troubleshoot it

`docker inspect NAME` looks the name up among containers, images, networks and volumes, and returns whichever it
finds. `nginx:1.30-alpine` is an image, and images have no `State`. Ask which type an object is, and look at the keys
the image document does have:

```bash
docker image inspect nginx:1.30-alpine | grep -E '^        "[A-Za-z]+": ' | cut -d'"' -f2 | tr '\n' ' '; echo
```

```text
Id RepoTags RepoDigests Comment Created Config Architecture Os Size RootFS Metadata Descriptor Identity 
```

## Fix it

Use the field that exists for the object you mean, and name the type explicitly so the script fails clearly when it
gets the wrong object:

```bash
docker container inspect --format '{{.State.Status}}' web
docker image inspect --format '{{.Os}}/{{.Architecture}}' nginx:1.30-alpine
```

```text
running
linux/amd64
```

`docker container inspect` refuses images (`No such container`), `docker image inspect` refuses containers: errors
instead of surprises.
