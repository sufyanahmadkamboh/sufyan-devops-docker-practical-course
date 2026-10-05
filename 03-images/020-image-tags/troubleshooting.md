<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 020 · Image tags · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The team wants a second image, the "Menu Board", and names it the way it is written in documents:

```bash
docker image tag cafe-menu:1.4.4 Menu-Board:1.0
```

```text
error parsing reference: "Menu-Board:1.0" is not a valid repository/tag: invalid reference format: repository name (library/Menu-Board) must be lowercase
```

## Troubleshoot it

`invalid reference format: repository name … must be lowercase`: the repository part of an image name may only contain
lowercase letters, digits, and the separators `.`, `_`, `-` and `/`. The **tag** may contain uppercase letters, but
not `+`, `/` or spaces, and must not start with `.` or `-`. The same error appears in `docker build -t`, `docker run` and Compose files.
Test a name before using it:

```bash
for name in Menu-Board:1.0 menu-board:1.0+build7 menu-board:1.0-build7; do
  if docker image tag cafe-menu:1.4.4 "$name" 2> /dev/null; then echo "valid:   $name"; else echo "invalid: $name"; fi
done
```

```text
invalid: Menu-Board:1.0
invalid: menu-board:1.0+build7
valid:   menu-board:1.0-build7
```

## Fix it

Use a lowercase repository name:

```bash
docker image tag cafe-menu:1.4.4 menu-board:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' menu-board
```
