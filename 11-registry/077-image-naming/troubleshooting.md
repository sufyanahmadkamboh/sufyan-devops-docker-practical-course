<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 077 · Image naming · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate names the image after the product's spelling:

```bash
docker tag busybox:1.37 localhost:5000/CafeTeam/CafeAPI:1.4.2 2>&1
```

```text
error parsing reference: "localhost:5000/CafeTeam/CafeAPI:1.4.2" is not a valid repository/tag: invalid reference format: repository name (CafeTeam/CafeAPI) must be lowercase
```

## Troubleshoot it

`invalid reference format: repository name … must be lowercase`: the registry part may contain capitals (host names are
case-insensitive), the repository path may not. Tags may (`1.4.2-RC1` is valid). Other `invalid reference format`
causes are characters outside the allowed set: a space, a second `:` in the tag, a leading `-`.

```bash
for name in cafe-api:1.4.2-RC1 cafe_api:1.4.2 "cafe api:1.4.2" cafe-api:1.4:2; do
  docker tag busybox:1.37 "$name" 2> /dev/null && echo "valid:   $name" || echo "invalid: $name"
done
docker image rm cafe-api:1.4.2-RC1 cafe_api:1.4.2 > /dev/null
```

```text
valid:   cafe-api:1.4.2-RC1
valid:   cafe_api:1.4.2
invalid: cafe api:1.4.2
invalid: cafe-api:1.4:2
```

## Fix it

```bash
docker tag busybox:1.37 localhost:5000/cafeteam/cafe-api:1.4.2
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep cafeteam
```
