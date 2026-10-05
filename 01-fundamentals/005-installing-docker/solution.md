<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 005 · Installing Docker · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Write a one-line health report of your installation: the client version, the server version, the number of running
containers and the number of images. Use only `--format` (no `grep`).

## Solution

```bash
echo "client $(docker version --format '{{.Client.Version}}'), server $(docker info --format '{{.ServerVersion}}'), $(docker info --format '{{.ContainersRunning}} running, {{.Images}} images')"
```

```text
client 29.4.3, server 29.4.3, 0 running, 20 images
```

`docker version` knows the client; `docker info` describes the engine.
