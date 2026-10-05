<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 050 · Container DNS · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker network create shop-net > /dev/null
docker run -d --name web --network shop-net nginx:1.30-alpine > /dev/null
docker ps --format '{{.Names}}'
```

## Demonstration

```bash
docker run --rm --network shop-net busybox:1.37 grep nameserver /etc/resolv.conf
```

```bash
docker run --rm --network shop-net busybox:1.37 nslookup web. 2>&1 | grep -A2 '^Name'
echo "web's IP: $(docker inspect web --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')"
```

```bash
docker run -d --name search-1 --network shop-net --network-alias search nginx:1.30-alpine > /dev/null
docker run -d --name search-2 --network shop-net --network-alias search nginx:1.30-alpine > /dev/null
docker run --rm --network shop-net busybox:1.37 nslookup search. 2>&1 | grep '^Address' | grep -v 127.0.0.11 | sort
```

## Hands-on lab

```bash
docker run --rm --network shop-net busybox:1.37 nslookup example.com 2>&1 | grep -m1 -A1 '^Name'
for c in search-1 search-2; do
  echo "$c $(docker inspect $c --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')"
done
```

## Break it

```bash
docker run -d --name api-v2 --network shop-net nginx:1.30-alpine > /dev/null
docker run --rm --network shop-net busybox:1.37 wget -qO /dev/null -T 5 http://api 2>&1
```

## Troubleshoot it

```bash
docker run --rm --network shop-net busybox:1.37 nslookup api. 2>&1 | grep -m1 -iE "NXDOMAIN|can't find|no answer"
docker run --rm --network shop-net busybox:1.37 nslookup api-v2. 2>&1 | grep -m1 -A1 '^Name'
```

```bash
docker inspect api-v2 --format '{{range $net, $cfg := .NetworkSettings.Networks}}{{$net}}: {{$cfg.DNSNames}}{{end}}'
```

## Fix it

```bash
docker network disconnect shop-net api-v2
docker network connect --alias api shop-net api-v2
docker run --rm --network shop-net busybox:1.37 wget -qO /dev/null -T 5 http://api && echo "reachable as api"
```

## Practice challenge

```bash
docker stop search-1 > /dev/null
count=$(docker run --rm --network shop-net busybox:1.37 nslookup search. 2>&1 | grep '^Address' | grep -vc 127.0.0.11)
[ "$count" -eq 1 ] && echo "one address: only the running search-2"
```

## Cleanup

```bash
docker rm -f web search-1 search-2 api-v2 > /dev/null
docker network rm shop-net > /dev/null
```
