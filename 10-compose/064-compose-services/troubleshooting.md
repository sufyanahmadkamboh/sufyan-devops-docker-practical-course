<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 064 · Services · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

More traffic: run two copies of the API.

```bash
docker compose up -d --scale api=2 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```text
Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint lesson-064-api-2 (b5ff8a2ebfe2758b37ebdb39d2d16dfbadb6119e46f1fb9e5a11bc8775083d96): Bind for 0.0.0.0:8080 failed: port is already allocated
```

## Troubleshoot it

`Bind for 0.0.0.0:8080 failed: port is already allocated`: the second replica asked for host port 8080, which the first
one already holds. A host port can belong to one container only. The failed replica was created but never started:

```bash
docker compose ps -a --format '{{.Name}}: {{.State}}'
```

```text
lesson-064-api-1: running
lesson-064-api-2: created
lesson-064-redis-1: running
```

## Fix it

Give the service a **range** of host ports: each replica takes a free one.

```bash
sed -i.bak 's/"8080:5000"/"8080-8081:5000"/' compose.yaml && rm compose.yaml.bak
docker compose up -d --scale api=2 2> /dev/null
docker compose ps --format '{{.Name}}  {{.Ports}}'
```

In production the replicas sit behind a reverse proxy or load balancer, and only the proxy publishes a port (the
capstone does this with Nginx).
