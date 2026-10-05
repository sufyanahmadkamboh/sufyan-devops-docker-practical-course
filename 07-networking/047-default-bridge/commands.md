<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 047 · The default bridge network · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
docker ps --filter name=web --format '{{.Names}} {{.Status}}'
```

## Demonstration

```bash
docker network inspect bridge --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'
```

```bash
ip=$(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')
echo "web is at $ip"
docker run --rm busybox:1.37 wget -qO- "http://$ip" | grep -o '<title>.*</title>'
```

## Hands-on lab

```bash
docker network inspect bridge --format 'gateway {{(index .IPAM.Config 0).Gateway}}'
docker run --rm busybox:1.37 wget -qO- "http://$(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')" | grep -o '<title>.*</title>'
```

## Break it

```bash
docker run --rm busybox:1.37 wget -qO- -T 5 http://web 2>&1
```

## Troubleshoot it

```bash
docker run --rm busybox:1.37 cat /etc/resolv.conf | grep nameserver
```

```bash
echo "before: $(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')"
docker rm -f web > /dev/null
docker run -d --name other nginx:1.30-alpine > /dev/null
docker run -d --name web nginx:1.30-alpine > /dev/null
echo "after:  $(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')"
docker rm -f other > /dev/null
```

## Fix it

```bash
docker network create shop-net > /dev/null
docker network connect shop-net web
docker run --rm --network shop-net busybox:1.37 wget -qO- http://web | grep -o '<title>.*</title>'
```

## Practice challenge

```bash
docker inspect web --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{"\n"}}{{end}}'
```

## Cleanup

```bash
docker rm -f web > /dev/null
docker network rm shop-net > /dev/null
```
