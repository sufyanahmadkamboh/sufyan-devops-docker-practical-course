<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 050 · Container DNS · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The team deploys a new version of the backend next to the old one, as `api-v2`. The clients are configured to call
`http://api`:

```bash
docker run -d --name api-v2 --network shop-net nginx:1.30-alpine > /dev/null
docker run --rm --network shop-net busybox:1.37 wget -qO /dev/null -T 5 http://api 2>&1
```

```text
wget: bad address 'api'
```

## Troubleshoot it

`bad address 'api'`: DNS has no record for `api`. Ask the DNS server directly, for both names:

```bash
docker run --rm --network shop-net busybox:1.37 nslookup api. 2>&1 | grep -m1 -iE "NXDOMAIN|can't find|no answer"
docker run --rm --network shop-net busybox:1.37 nslookup api-v2. 2>&1 | grep -m1 -A1 '^Name'
```

```text
** server can't find api.: NXDOMAIN
Name:	api-v2
Address: 172.18.0.5
```

Docker records the DNS names it registers for a container on each network. `api` is not one of them:

```bash
docker inspect api-v2 --format '{{range $net, $cfg := .NetworkSettings.Networks}}{{$net}}: {{$cfg.DNSNames}}{{end}}'
```

```text
shop-net: [api-v2 2a81160f13a9]
```

The container name and the short container ID, nothing else. The clients ask for a name that no container on the
network has.

## Fix it

Give the container the DNS name its clients use, as a network alias (connect again with `--alias`):

```bash
docker network disconnect shop-net api-v2
docker network connect --alias api shop-net api-v2
docker run --rm --network shop-net busybox:1.37 wget -qO /dev/null -T 5 http://api && echo "reachable as api"
```

Starting it with `--network-alias api` would have avoided the problem from the start. An alias also makes
switching versions easy: move the alias from the old container to the new one, and the clients never change.
