# Lesson 047 · The default bridge network

> Level 8 · Networking · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Containers started without `--network` join the **default bridge** network (`bridge`, the `docker0` interface on the
host). Containers on it can reach each other **by IP address**, but **not by name**: the default bridge has no
service discovery. IP addresses change whenever a container is recreated, so the default bridge is fine for single
containers and a trap for applications made of several containers.

## Visual

```text
  default "bridge" network 172.17.0.0/16 (docker0 = 172.17.0.1)

  ┌───────────────────┐                      ┌───────────────────┐
  │ web  (nginx)      │ ◀── http://172.17.0.2 ── │ client (busybox)  │   ✔ by IP
  │ 172.17.0.2        │                      │ 172.17.0.3        │
  └───────────────────┘ ◀── http://web ─────── └───────────────────┘   ✘ "bad address 'web'"
                                                                       (no DNS for container names)
  recreate "web" → it may get another IP → every hard-coded IP breaks
```

## Lab setup

No files are needed: nginx serves its default page.

<!-- test: contains=web -->
```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
docker ps --filter name=web --format '{{.Names}} {{.Status}}'
```

## Demonstration

Which containers are on the default bridge, and with which addresses:

<!-- test: contains=web; output -->
```bash
docker network inspect bridge --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'
```

```text
web 172.17.0.2/16
```

Another container on the same network can reach `web` by its IP address:

<!-- test: contains=Welcome to nginx; output; retry=5 -->
```bash
ip=$(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')
echo "web is at $ip"
docker run --rm busybox:1.37 wget -qO- "http://$ip" | grep -o '<title>.*</title>'
```

```text
web is at 172.17.0.2
<title>Welcome to nginx!</title>
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker network inspect bridge` | the network's configuration and the containers attached to it |
| `--format '{{range .Containers}}…{{end}}'` | loop over the attached containers |
| `docker inspect C --format '{{.NetworkSettings.Networks.bridge.IPAddress}}'` | a container's IP on the `bridge` network |
| `wget -qO- URL` | (BusyBox) fetch a URL and print it, quietly |

## Hands-on lab

**Instructions.** Find the gateway address of the default bridge network, and show that `web` answers on its IP from a
second container.

**Expected result.** A gateway such as `172.17.0.1`, and nginx's welcome page title.

**Verification.**

<!-- test: contains=gateway; contains=Welcome to nginx; retry=5 -->
```bash
docker network inspect bridge --format 'gateway {{(index .IPAM.Config 0).Gateway}}'
docker run --rm busybox:1.37 wget -qO- "http://$(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')" | grep -o '<title>.*</title>'
```

## Break it

Use the container's name instead of its IP, as you would in an application's configuration:

<!-- test: fail; anyof=bad address||can't connect||timed out; output -->
```bash
docker run --rm busybox:1.37 wget -qO- -T 5 http://web 2>&1
```

```text
wget: bad address 'web'
```

## Troubleshoot it

`bad address 'web'`: the name `web` could not be resolved. The container exists and is running, so it is not about
`web` itself. (On some networks the host's DNS server answers for unknown names, and you see
`can't connect to remote host (127.0.53.53)` or a timeout instead: the same problem, the name did not lead to the
`web` container.) Look at which DNS server the client uses and whether it knows `web`:

<!-- test: contains=nameserver; output -->
```bash
docker run --rm busybox:1.37 cat /etc/resolv.conf | grep nameserver
```

```text
nameserver 192.168.65.7
```

On the default bridge, a container gets the host's DNS servers (on Docker Desktop, the VM's resolver), which know
public names but nothing about containers. Docker's own DNS server for container names only serves **user-defined**
networks. And the IP is not a reliable fallback: recreate `web` and it can get a different one:

<!-- test: contains=before; contains=after; output -->
```bash
echo "before: $(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')"
docker rm -f web > /dev/null
docker run -d --name other nginx:1.30-alpine > /dev/null
docker run -d --name web nginx:1.30-alpine > /dev/null
echo "after:  $(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')"
docker rm -f other > /dev/null
```

```text
before: 172.17.0.2
after:  172.17.0.3
```

## Fix it

Put the containers on a user-defined network (lesson 048): Docker's DNS then resolves container names.

<!-- test: contains=Welcome to nginx; output; retry=5 -->
```bash
docker network create shop-net > /dev/null
docker network connect shop-net web
docker run --rm --network shop-net busybox:1.37 wget -qO- http://web | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

The old `--link` option made names work on the default bridge; it is deprecated and should not be used any more.

## Practice challenge

`web` is now on two networks. Show both of its IP addresses, one per network.

<details>
<summary>Solution</summary>

<!-- test: contains=shop-net; contains=bridge; output -->
```bash
docker inspect web --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{"\n"}}{{end}}'
```

```text
bridge 172.17.0.3
shop-net 172.18.0.2
```

A container gets one interface and one address per network it is connected to.

</details>

## Real-world example

A developer starts a database and an API with plain `docker run` and configures the API with the database's IP. It
works until the laptop restarts and the containers come back in a different order: the IPs swap and the API connects
to nothing. Moving both containers to a user-defined network and configuring the API with the name `db` fixes it for
good; Docker Compose (lesson 065) creates such a network automatically.

## Recap

- Containers without `--network` join the default `bridge` network.
- On the default bridge, containers reach each other by IP only; names give `bad address`.
- Container IPs are not stable across recreation: never hard-code them.
- User-defined networks add DNS for container names (lesson 048).

## Cleanup

<!-- test -->
```bash
docker rm -f web > /dev/null
docker network rm shop-net > /dev/null
```

Next: [Lesson 048 · Custom networks](../048-custom-networks/README.md)
