<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 048 · Custom networks · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The proxy tries to reach the database directly:

```bash
docker run --rm --network frontend-net busybox:1.37 wget -qO /dev/null -T 3 http://db 2>&1
```

```text
wget: bad address 'db'
```

## Troubleshoot it

`bad address 'db'`: Docker's DNS only answers names of containers **on the same network** as the one asking. Check
which networks each container is on:

```bash
for c in db api; do
  echo "$c: $(docker inspect $c --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}')"
done
```

```text
db: backend-net 
api: backend-net frontend-net 
```

`db` is only on `backend-net`; the proxy is only on `frontend-net`. Here that is the **intended** design: the database
should not be reachable from the edge. If a container really needs the access, connect it to the network; otherwise,
the fix is in the application: the proxy talks to the API, and the API talks to the database.

## Fix it

When a container is on the wrong network (a common mistake), connect it to the right one; disconnect it from the
networks it should not be on:

<!-- test: contains=worker -> db: ok; output; retry=5 -->
```bash
docker run -d --name worker --network frontend-net alpine:3.23 sleep 300 > /dev/null
docker network connect backend-net worker
docker network disconnect frontend-net worker
docker exec worker wget -qO /dev/null -T 3 http://db && echo "worker -> db: ok"
```

```text
worker -> db: ok
```
