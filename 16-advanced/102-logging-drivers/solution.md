<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 102 · Logging drivers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Print a table of every running container with its logging driver and its `max-size` option, showing `unlimited` when
there is none.

## Solution

```bash
docker ps -q | xargs docker inspect --format \
  '{{.Name}} {{.HostConfig.LogConfig.Type}} {{with index .HostConfig.LogConfig.Config "max-size"}}{{.}}{{else}}unlimited{{end}}'
```

```text
/quiet local 10m
/rotated json-file 1m
/chatty json-file unlimited
```

`{{with X}}…{{else}}…{{end}}` prints the value when it exists and is not empty, and the fallback otherwise.
