# Lesson 046 · Networking fundamentals

> Level 8 · Networking · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Every container gets its own **network namespace**: its own network interfaces, IP addresses, routing table and ports.
Docker connects that namespace to a **network** chosen with `--network`. The three built-in networks show the three
basic choices: `bridge` (the default: a private network behind the host, with outgoing access), `host` (no isolation:
the container uses the host's network directly) and `none` (no network at all, only loopback).

## Visual

```text
                       Docker host
 ┌───────────────────────────────────────────────────────────────────────┐
 │                                                                       │
 │  bridge (default)              host                    none           │
 │  ┌──────────────┐              ┌──────────────┐        ┌───────────┐  │
 │  │ container A  │              │ container C  │        │ container │  │
 │  │ lo  eth0     │              │ uses the     │        │ lo only   │  │
 │  │ 172.17.0.2   │              │ host's       │        │ no eth0   │  │
 │  └──────┬───────┘              │ interfaces   │        └───────────┘  │
 │         │ veth pair            └──────────────┘                       │
 │  ┌──────┴────────────────┐                                            │
 │  │ docker0 172.17.0.1    │──── NAT ────▶ host interface ──▶ internet  │
 │  └───────────────────────┘                                            │
 └───────────────────────────────────────────────────────────────────────┘
```

| Network | Driver | Isolation | Typical use |
|---|---|---|---|
| `bridge` | `bridge` | own IP on a private subnet; outgoing traffic through NAT | the default for single containers |
| user-defined bridge | `bridge` | the same, plus DNS between containers | applications with several containers (lesson 048) |
| `host` | `host` | none: shares the host's interfaces and ports | special cases (network tools, performance), Linux only in full |
| `none` | `null` | no interface except loopback | jobs that must not talk to anything |

## Lab setup

No files are needed: this lesson inspects networks directly.

## Demonstration

The networks every Docker engine starts with:

<!-- test: contains=bridge; contains=host; contains=none; output -->
```bash
docker network ls
```

```text
NETWORK ID     NAME      DRIVER    SCOPE
9c28fbb933f7   bridge    bridge    local
6278dc274ea1   host      host      local
3d5e01f105cb   none      null      local
```

A container on the default network has a loopback interface and an `eth0` with a private address:

<!-- test: contains=eth0; output -->
```bash
docker run --rm alpine:3.23 sh -c "ip -4 -o addr | awk '{print \$2, \$4}'"
```

```text
lo 127.0.0.1/8
eth0 172.17.0.2/16
```

Its routing table sends everything else to the bridge's gateway (the host side of the network):

<!-- test: contains=default via; output -->
```bash
docker run --rm alpine:3.23 ip route
```

```text
default via 172.17.0.1 dev eth0 
172.17.0.0/16 dev eth0 scope link  src 172.17.0.2 
```

With `--network none`, only loopback is left:

<!-- test: contains=lo; absent=eth0; output -->
```bash
docker run --rm --network none alpine:3.23 sh -c "ip -4 -o addr | awk '{print \$2, \$4}'"
```

```text
lo 127.0.0.1/8
```

## Command breakdown

| Command / flag | What it does |
|---|---|
| `docker network ls` | list the networks of the engine |
| `--network NAME` | attach the new container to that network (default: `bridge`) |
| `ip -4 -o addr` | the container's IPv4 addresses, one line per interface |
| `ip route` | the container's routing table; `default via` is its gateway |

## Hands-on lab

**Instructions.** Show the IPv4 address and the default gateway of a container on the default `bridge` network, and
the subnet of that network as Docker reports it.

**Expected result.** The address is inside the subnet, and the gateway is the subnet's first address (for example
`172.17.0.2`, gateway `172.17.0.1`, subnet `172.17.0.0/16`; the numbers can differ on your engine).

**Verification.**

<!-- test: contains=subnet -->
```bash
docker run --rm alpine:3.23 sh -c "ip -4 -o addr show eth0 | awk '{print \"address\", \$4}'; ip route | awk '/default/ {print \"gateway\", \$3}'"
docker network inspect bridge --format 'subnet {{(index .IPAM.Config 0).Subnet}}'
```

## Break it

A nightly job downloads a file. Someone hardened it by starting it with `--network none`:

<!-- test: fail; contains=bad address; output -->
```bash
docker run --rm --network none alpine:3.23 wget -q -T 5 -O /dev/null http://example.com 2>&1
```

```text
wget: bad address 'example.com'
```

## Troubleshoot it

`bad address 'example.com'`: the name could not be resolved, because the container has no network at all, not even a
DNS server to ask. The first question for any connection problem in a container is "which network is it on?":

<!-- test: contains=none; output -->
```bash
docker run -d --name job --network none alpine:3.23 sleep 60 > /dev/null
docker inspect job --format 'network mode: {{.HostConfig.NetworkMode}}'
docker exec job ip -4 -o addr | awk '{print $2, $4}'
docker rm -f job > /dev/null
```

```text
network mode: none
lo 127.0.0.1/8
```

Only `lo`: nothing can leave the container.

## Fix it

Give the job the network it needs (here the default bridge, which allows outgoing connections):

<!-- test: contains=downloaded; retry=3 -->
```bash
docker run --rm alpine:3.23 sh -c 'wget -q -T 10 -O /dev/null http://example.com && echo downloaded'
```

`--network none` is still the right choice for jobs that only process local files: no network means nothing to attack
and nothing to leak.

## Practice challenge

Start two containers on the default network and show that each one has its **own** IP address, but both use the same
gateway.

<details>
<summary>Solution</summary>

<!-- test: contains=one; contains=two; output -->
```bash
docker run -d --name one alpine:3.23 sleep 60 > /dev/null
docker run -d --name two alpine:3.23 sleep 60 > /dev/null
for c in one two; do
  echo "$c: $(docker inspect $c --format '{{.NetworkSettings.Networks.bridge.IPAddress}} via {{.NetworkSettings.Networks.bridge.Gateway}}')"
done
docker rm -f one two > /dev/null
```

```text
one: 172.17.0.2 via 172.17.0.1
two: 172.17.0.3 via 172.17.0.1
```

Each container has its own network namespace and address; the bridge's gateway is shared.

</details>

## Real-world example

A team runs a PDF rendering service that processes untrusted uploads. They run each rendering job with
`--network none`: even if a malicious document exploits the renderer, the container cannot download a payload or send
data anywhere. The web API that receives the uploads runs on a normal network, because it must accept connections.

## Recap

- Each container has its own network namespace: interfaces, IP address, routes, ports.
- `bridge` (default): private address, outgoing access through NAT; `host`: the host's network; `none`: loopback only.
- `docker network ls`, `docker inspect … .NetworkSettings` and `ip addr`/`ip route` inside the container show where
  a container is connected.
- For any connection problem, first check which network the container is on.

## Cleanup

Nothing to clean: every container was removed.

Next: [Lesson 047 · The default bridge network](../047-default-bridge/README.md)
