<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 021 · The danger of the latest tag · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague builds a new version, also without a tag, and a second container is started "the same way":

```bash
docker build -q --build-arg VERSION=2.0 -t cafe-menu . > /dev/null
docker run -d --name menu-b cafe-menu > /dev/null
echo "menu-a: $(docker exec menu-a cat /version)"
echo "menu-b: $(docker exec menu-b cat /version)"
```

```text
menu-a: cafe menu 1.0
menu-b: cafe menu 2.0
```

Two containers, both started with `docker run cafe-menu`, run different software. If `menu-b` has a bug, which code is
it, and what do you roll back to? "latest" does not say.

## Troubleshoot it

Compare the image each container was started *by name* with the image *ID* it really runs:

```bash
docker container ls --format '{{.Names}}  name={{.Image}}' --filter name=menu-
for c in menu-a menu-b; do echo "$c runs $(docker container inspect --format '{{.Image}}' $c | cut -c1-19)"; done
echo "cafe-menu:latest is now $(docker image inspect --format '{{.Id}}' cafe-menu:latest | cut -c1-19)"
```

```text
menu-b  name=cafe-menu
menu-a  name=7448c93a9a88
menu-a runs sha256:7448c93a9a88
menu-b runs sha256:b1ed18ebfcf3
cafe-menu:latest is now sha256:b1ed18ebfcf3
```

`menu-a` was started from `cafe-menu`, but `latest` has moved since: the old image lost its name and Docker can only
show its ID. The tag tells you nothing reliable about what is running; only the image ID or digest does.

## Fix it

Give every build an explicit version tag, and deploy that tag:

```bash
docker build -q --build-arg VERSION=2.0 -t cafe-menu:2.0 . > /dev/null
docker run -d --name menu-v2 cafe-menu:2.0 > /dev/null
echo "menu-v2: $(docker exec menu-v2 cat /version)"
```

`docker run cafe-menu:2.0` runs 2.0 today, tomorrow and on every server. Pin base images the same way (`FROM
alpine:3.23`, never `FROM alpine`), or by digest for complete reproducibility (lesson 018).
