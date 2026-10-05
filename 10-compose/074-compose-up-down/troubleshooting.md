<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 074 · up, down and the project lifecycle · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The team no longer needs the `worker` service and deletes it from the file. Everyone runs `up` as usual:

```bash
awk '/^  worker:/ { skip = 1; next } /^[^ ]/ { skip = 0 } skip && /^    / { next } { print }' compose.yaml > compose.new
mv compose.new compose.yaml
docker compose config --services
docker compose up -d 2>&1 | grep -i orphan
```

```text
api
redis
time="2026-10-05T19:15:52+02:00" level=warning msg="Found orphan containers ([lesson-074-worker-1]) for this project. If you removed or renamed this service in your compose file, you can run this command with the --remove-orphans flag to clean it up."
```

## Troubleshoot it

A warning, not an error, so it is easy to miss. The old container still runs, uses resources, and (for a real worker)
may still be processing jobs with old code:

```bash
docker ps --filter label=com.docker.compose.project=lesson-074 --format '{{.Names}}: {{.Status}}'
```

```text
lesson-074-worker-1: Up 1 second
lesson-074-redis-1: Up 1 second
lesson-074-api-1: Up 1 second
```

Compose finds a project's containers through the `com.docker.compose.project` label; a container whose service is no
longer in the file is an **orphan**, and Compose does not remove it unless told to.

## Fix it

```bash
docker compose up -d --remove-orphans 2> /dev/null
docker ps --filter label=com.docker.compose.project=lesson-074 --format '{{.Names}}'
```

```text
lesson-074-redis-1
lesson-074-api-1
```
