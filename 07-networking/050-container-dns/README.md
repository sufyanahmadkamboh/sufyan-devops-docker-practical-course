# Lesson 050 · Container DNS

> Level 8 · Networking · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

On a user-defined network, every container uses Docker's **embedded DNS server** at `127.0.0.11`. It answers the names
of the containers on the same network (their **container names** and **network aliases**) and forwards every other
name (`example.com`) to the host's DNS servers. Knowing exactly which names it knows explains most "could not resolve
host" errors between containers.

## Visual

```text
  shop-net
 ┌────────────────────────────────────────────────────────────────────────────┐
 │  client                           Docker embedded DNS 127.0.0.11           │
 │  /etc/resolv.conf:                ┌────────────────────────────────────┐   │
 │    nameserver 127.0.0.11 ───────▶ │ web        → 172.20.0.2            │   │
 │                                   │ search     → 172.20.0.3, 172.20.0.4│   │  ← alias on two containers
 │                                   │ other name → forwarded to the host │───┼──▶ host DNS → internet
 │                                   └────────────────────────────────────┘   │
 └────────────────────────────────────────────────────────────────────────────┘
  known: container names, --network-alias          not known: containers on other networks, stopped containers
```

## Lab setup

<!-- test: contains=web -->
```bash
docker network create shop-net > /dev/null
docker run -d --name web --network shop-net nginx:1.30-alpine > /dev/null
docker ps --format '{{.Names}}'
```

## Demonstration

A container on `shop-net` asks Docker's DNS server:

<!-- test: contains=127.0.0.11; output -->
```bash
docker run --rm --network shop-net busybox:1.37 grep nameserver /etc/resolv.conf
```

```text
nameserver 127.0.0.11
```

It resolves `web` to the container's address on this network:

<!-- test: contains=Address; output -->
```bash
docker run --rm --network shop-net busybox:1.37 nslookup web 2>&1 | grep -A2 '^Name'
echo "web's IP: $(docker inspect web --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')"
```

```text
Name:	web
Address: 172.18.0.2

web's IP: 172.18.0.2
```

A **network alias** is an extra name; when several containers share one, DNS returns all of them (simple round-robin
load spreading):

<!-- test: contains=Address; output -->
```bash
docker run -d --name search-1 --network shop-net --network-alias search nginx:1.30-alpine > /dev/null
docker run -d --name search-2 --network shop-net --network-alias search nginx:1.30-alpine > /dev/null
docker run --rm --network shop-net busybox:1.37 nslookup search 2>&1 | grep '^Address' | grep -v 127.0.0.11 | sort
```

```text
Address: 172.18.0.3
Address: 172.18.0.4
```

## Command breakdown

| Command / flag | What it does |
|---|---|
| `nslookup NAME` | (BusyBox) ask the configured DNS server for NAME |
| `/etc/resolv.conf` | the DNS configuration of the container (`127.0.0.11` on user-defined networks) |
| `--network-alias NAME` | an extra DNS name for the container on that network; may be shared |
| `docker inspect C --format '{{…DNSNames}}'` | the names Docker's DNS answers for C on each network |
| `--dns IP` | the server that Docker's DNS forwards external names to, for this container |

## Hands-on lab

**Instructions.** Show that the embedded DNS also resolves external names, by looking up `example.com` from a
container on `shop-net`, and that `search` resolves to the two addresses of `search-1` and `search-2`.

**Expected result.** An address for `example.com`, and the same two addresses as
`docker inspect search-1 search-2`.

**Verification.**

<!-- test: contains=example.com; contains=search -->
```bash
docker run --rm --network shop-net busybox:1.37 nslookup example.com 2>&1 | grep -m1 -A1 '^Name'
for c in search-1 search-2; do
  echo "$c $(docker inspect $c --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')"
done
```

## Break it

The team deploys a new version of the backend next to the old one, as `api-v2`. The clients are configured to call
`http://api`:

<!-- test: fail; contains=bad address; output -->
```bash
docker run -d --name api-v2 --network shop-net nginx:1.30-alpine > /dev/null
docker run --rm --network shop-net busybox:1.37 wget -qO /dev/null -T 5 http://api 2>&1
```

```text
wget: bad address 'api'
```

## Troubleshoot it

`bad address 'api'`: DNS has no record for `api`. Ask the DNS server directly, for both names:

<!-- test: contains=NXDOMAIN; output -->
```bash
docker run --rm --network shop-net busybox:1.37 nslookup api 2>&1 | grep -m1 NXDOMAIN
docker run --rm --network shop-net busybox:1.37 nslookup api-v2 2>&1 | grep -m1 -A1 '^Name'
```

```text
** server can't find api: NXDOMAIN
Name:	api-v2
Address: 172.18.0.5
```

Docker records the DNS names it registers for a container on each network. `api` is not one of them:

<!-- test: contains=api-v2; output -->
```bash
docker inspect api-v2 --format '{{range $net, $cfg := .NetworkSettings.Networks}}{{$net}}: {{$cfg.DNSNames}}{{end}}'
```

```text
shop-net: [api-v2 84c474171932]
```

The container name and the short container ID, nothing else. The clients ask for a name that no container on the
network has.

## Fix it

Give the container the DNS name its clients use, as a network alias (connect again with `--alias`):

<!-- test: contains=reachable as api; retry=5 -->
```bash
docker network disconnect shop-net api-v2
docker network connect --alias api shop-net api-v2
docker run --rm --network shop-net busybox:1.37 wget -qO /dev/null -T 5 http://api && echo "reachable as api"
```

Starting it with `--network-alias api` would have avoided the problem from the start. An alias also makes
switching versions easy: move the alias from the old container to the new one, and the clients never change.

## Practice challenge

Stop `search-1` and look up `search` again. What does DNS return now, and what does that mean for clients?

<details>
<summary>Solution</summary>

<!-- test: contains=one address; output -->
```bash
docker stop search-1 > /dev/null
count=$(docker run --rm --network shop-net busybox:1.37 nslookup search 2>&1 | grep '^Address' | grep -vc 127.0.0.11)
[ "$count" -eq 1 ] && echo "one address: only the running search-2"
```

```text
one address: only the running search-2
```

Docker's DNS only returns running containers, so clients that resolve the name again are sent to `search-2`. Clients
that cached the old address still fail: DNS round-robin is not a health-checked load balancer (Compose and Kubernetes
services build on the same idea with more care).

</details>

## Real-world example

A team scales a stateless worker to three containers that share the alias `worker` on their network. A producer that
resolves `worker` on every connection spreads its jobs over the three. When they migrate to Kubernetes, the same idea
becomes a Service name: clients keep using a stable name while the containers behind it come and go.

## Recap

- On user-defined networks, containers use Docker's embedded DNS at `127.0.0.11`.
- It knows container names and network aliases on the same network, and forwards all other names.
- `docker inspect … DNSNames` lists exactly which names resolve; add others with `--network-alias`.
- Several containers can share an alias: DNS returns all running ones.

## Cleanup

<!-- test -->
```bash
docker rm -f web search-1 search-2 api-v2 > /dev/null
docker network rm shop-net > /dev/null
```

Next: [Lesson 051 · EXPOSE vs publishing ports](../051-expose-vs-publish/README.md)
