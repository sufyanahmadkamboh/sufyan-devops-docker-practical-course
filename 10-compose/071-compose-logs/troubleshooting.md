<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 071 · Logs · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The same worker, but written the "traditional" way: it appends to a log file.

```bash
docker compose -p lesson-071-file -f broken/compose.yaml up -d 2> /dev/null
sleep 5
docker compose -p lesson-071-file -f broken/compose.yaml logs worker
echo "lines: $(docker compose -p lesson-071-file -f broken/compose.yaml logs worker | wc -l)"
```

```text
lines: 0
```

## Troubleshoot it

The container is running, but its log is empty. Docker only sees stdout and stderr; the process writes somewhere else.
Look inside the container:

```bash
docker compose -p lesson-071-file -f broken/compose.yaml exec worker ls -l /var/log/worker.log
docker compose -p lesson-071-file -f broken/compose.yaml exec worker tail -2 /var/log/worker.log
```

```text
-rw-r--r--    1 root     root            76 Oct  5 17:14 /var/log/worker.log
worker: job 3 done
worker: job 4 done
```

The log exists only inside the container: `docker logs`, log collectors and dashboards cannot see it, it grows until the
disk is full, and it disappears with the container.

## Fix it

Write to stdout. When an application can only write to a file, point that file at stdout (the official Nginx image does
exactly this: `/var/log/nginx/access.log` is a link to `/dev/stdout`):

```bash
docker compose -p lesson-071-file -f broken/compose.yaml down 2> /dev/null
sed -i.bak 's# >> /var/log/worker.log##' broken/compose.yaml && rm broken/compose.yaml.bak
docker compose -p lesson-071-file -f broken/compose.yaml up -d 2> /dev/null
sleep 5
docker compose -p lesson-071-file -f broken/compose.yaml logs --no-log-prefix worker
```

```text
...
worker: job 2 done
worker: job 3 done
```
