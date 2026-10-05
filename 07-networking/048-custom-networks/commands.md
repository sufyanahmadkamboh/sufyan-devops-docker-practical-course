<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 048 · Custom networks · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker network create --subnet 172.30.1.0/24 frontend-net
docker network create --subnet 172.30.2.0/24 backend-net
docker network ls --filter name=-net
```

## Demonstration

```bash
docker run -d --name db --network backend-net nginx:1.30-alpine > /dev/null
docker run -d --name api --network frontend-net nginx:1.30-alpine > /dev/null
docker network connect backend-net api
docker inspect api --format '{{range $name, $net := .NetworkSettings.Networks}}api on {{$name}}: {{$net.IPAddress}}{{"\n"}}{{end}}'
```

```bash
docker exec api wget -qO /dev/null -T 3 http://db && echo "api -> db: ok"
docker run --rm --network frontend-net busybox:1.37 wget -qO /dev/null -T 3 http://api && echo "proxy -> api: ok"
```

## Hands-on lab

```bash
docker network inspect backend-net --format '{{(index .IPAM.Config 0).Subnet}} via {{(index .IPAM.Config 0).Gateway}}'
docker network inspect backend-net --format '{{range .Containers}}{{.Name}} {{end}}'
```

## Break it

```bash
docker run --rm --network frontend-net busybox:1.37 wget -qO /dev/null -T 3 http://db 2>&1
```

## Troubleshoot it

```bash
for c in db api; do
  echo "$c: $(docker inspect $c --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}')"
done
```

## Fix it

```bash
docker run -d --name worker --network frontend-net alpine:3.23 sleep 300 > /dev/null
docker network connect backend-net worker
docker network disconnect frontend-net worker
docker exec worker wget -qO /dev/null -T 3 http://db && echo "worker -> db: ok"
```

## Practice challenge

```bash
docker network create --subnet 10.10.0.0/24 lab-net > /dev/null
docker run --rm --network lab-net --ip 10.10.0.50 alpine:3.23 sh -c "ip -4 -o addr show eth0 | awk '{print \$4}'"
docker network rm lab-net > /dev/null
```

## Cleanup

```bash
docker rm -f db api worker > /dev/null
docker network rm frontend-net backend-net > /dev/null
```
