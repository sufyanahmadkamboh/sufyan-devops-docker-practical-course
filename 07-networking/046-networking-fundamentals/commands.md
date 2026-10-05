<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 046 · Networking fundamentals · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker network ls
```

```bash
docker run --rm alpine:3.23 sh -c "ip -4 -o addr | awk '{print \$2, \$4}'"
```

```bash
docker run --rm alpine:3.23 ip route
```

```bash
docker run --rm --network none alpine:3.23 sh -c "ip -4 -o addr | awk '{print \$2, \$4}'"
```

## Hands-on lab

```bash
docker run --rm alpine:3.23 sh -c "ip -4 -o addr show eth0 | awk '{print \"address\", \$4}'; ip route | awk '/default/ {print \"gateway\", \$3}'"
docker network inspect bridge --format 'subnet {{(index .IPAM.Config 0).Subnet}}'
```

## Break it

```bash
docker run --rm --network none alpine:3.23 wget -q -T 5 -O /dev/null http://example.com 2>&1
```

## Troubleshoot it

```bash
docker run -d --name job --network none alpine:3.23 sleep 60 > /dev/null
docker inspect job --format 'network mode: {{.HostConfig.NetworkMode}}'
docker exec job ip -4 -o addr | awk '{print $2, $4}'
docker rm -f job > /dev/null
```

## Fix it

```bash
docker run --rm alpine:3.23 sh -c 'wget -q -T 10 -O /dev/null http://example.com && echo downloaded'
```

## Practice challenge

```bash
docker run -d --name one alpine:3.23 sleep 60 > /dev/null
docker run -d --name two alpine:3.23 sleep 60 > /dev/null
for c in one two; do
  echo "$c: $(docker inspect $c --format '{{.NetworkSettings.Networks.bridge.IPAddress}} via {{.NetworkSettings.Networks.bridge.Gateway}}')"
done
docker rm -f one two > /dev/null
```
