<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 066 · Volumes in Compose · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague's copy of the file mounts the volume but forgot to declare it at the top level:

```bash
docker compose -f broken/compose.yaml config 2>&1
```

```text
service "redis" refers to undefined volume redis-data: invalid compose project
```

## Troubleshoot it

`refers to undefined volume redis-data`: in a service, `redis-data:/data` (a name, not a path) means a **named volume**,
and every named volume must be declared under the top-level `volumes:` key. Compose checks this before creating
anything. Compare the two files:

```bash
diff broken/compose.yaml compose.yaml || true
```

```text
12a13,15
> 
> volumes:
>   redis-data:                                 # Compose creates it as lesson-066_redis-data
```

## Fix it

Add the declaration (here: copy the correct file) and validate:

```bash
cp compose.yaml broken/compose.yaml
docker compose -f broken/compose.yaml config --volumes
```
