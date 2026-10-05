<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 010 · Container names · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Start a second container with the name `proxy`, which an existing container already has:

```bash
docker run -d --name proxy nginx:1.30-alpine 2>&1
```

```text
docker: Error response from daemon: Conflict. The container name "/proxy" is already in use by container "4389271662cdb393aa8e21820fbe5eb4eb5f267e8190cfeef4f25dcf862b585b". You have to remove (or rename) that container to be able to reuse that name.

Run 'docker run --help' for more information
```

## Troubleshoot it

`Conflict. The container name "/proxy" is already in use by container "…"`. The error names the container that holds
the name. This happens most often with a container that has **exited**: it no longer shows in `docker ps`, but it still
owns its name. Check all containers with that exact name:

```bash
docker ps -a --filter name=^proxy$ --format '{{.Names}}: {{.Status}} (created {{.RunningFor}})'
```

## Fix it

Decide: is the old container still needed? If not, remove it and reuse the name; if it is, choose another name.

```bash
docker rm -f proxy > /dev/null
docker run -d --name proxy nginx:1.30-alpine > /dev/null
docker ps --filter name=^proxy$ --format '{{.Names}}: {{.Status}}'
```

Scripts that start the same container again and again usually do `docker rm -f NAME 2>/dev/null; docker run --name
NAME …`, or use `docker run --rm` so the name is freed when the container exits.
