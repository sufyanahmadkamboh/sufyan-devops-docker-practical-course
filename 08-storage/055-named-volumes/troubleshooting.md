<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 055 · Named volumes · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Delete the volume to "start fresh":

```bash
docker volume rm app-data 2>&1
```

```text
Error response from daemon: remove app-data: volume is in use - [c7384d8caa0fb7e6c44c4e013e5142c13d628d21535f8ed2d71a7f86a724c055]
```

## Troubleshoot it

`volume is in use - [ID]`: Docker refuses to delete a volume that a container (running **or stopped**) references; the
ID in brackets is that container. Find it by name:

```bash
docker ps -a --filter volume=app-data --format '{{.ID}} {{.Names}} {{.Status}}'
```

```text
c7384d8caa0f writer Up 2 seconds
```

This protection is deliberate: removing a database's volume by accident is how data is lost.

## Fix it

Decide first whether the data may really go. If yes, remove the container, then the volume:

```bash
docker rm -f writer > /dev/null
docker volume rm app-data > /dev/null && echo "volume removed"
```

```text
volume removed
```

`docker rm -v CONTAINER` removes a container together with its **anonymous** volumes; named volumes always need an
explicit `docker volume rm`.
