<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 063 · Your first Compose file · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague's version of the file has one space too many before `environment:`:

```bash
docker compose -f broken/compose.yaml config 2>&1
```

```text
yaml: while parsing a block mapping at line 2, column 5: line 5, column 6: did not find expected key
```

## Troubleshoot it

The error comes from the YAML parser, before Compose looks at any service. It names two places: the mapping it was
reading (line 2, the keys of `api`) and where it got lost (line 5, column 6). Look at those lines with visible spaces:

```bash
sed -n '2,6p' broken/compose.yaml | sed 's/ /·/g'
```

```text
··api:
····build:·.
····ports:
······-·"8080:5000"
·····environment:
```

`build` and `ports` start at column 5; `environment` starts at column 6. Keys of the same mapping must line up exactly.

## Fix it

Indent `environment:` like its siblings, and validate again:

```bash
sed -i.bak 's/^     environment:/    environment:/' broken/compose.yaml && rm broken/compose.yaml.bak
docker compose -f broken/compose.yaml config --services
```

Run `docker compose config` after every edit: it catches syntax and schema errors before anything starts. Editors
with YAML support (and the Compose schema) mark these mistakes as you type.
