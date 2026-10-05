# Lesson 048 · Custom networks

> Level 8 · Networking · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

A **user-defined network** (`docker network create NAME`) is a bridge network you own. Compared with the default
bridge it gives you three things: **DNS** (containers find each other by name), **isolation** (only the containers you
attach can talk to each other) and **control** (you choose the subnet, and connect or disconnect running containers).
Every multi-container application should get its own network.

## Visual

```text
  frontend-net 172.30.1.0/24                     backend-net 172.30.2.0/24
 ┌──────────────────────────────────┐          ┌──────────────────────────────────┐
 │  proxy ─────────▶ api ───────────┼──────────┼──▶ api ─────────▶ db             │
 │                   (on both)      │          │   (same container)               │
 └──────────────────────────────────┘          └──────────────────────────────────┘
   proxy can reach api, not db                    db is reachable only from backend-net

 docker network create · connect · disconnect · inspect · rm
```

## Lab setup

No files are needed. Create two networks with chosen subnets:

<!-- test: contains=frontend-net; contains=backend-net -->
```bash
docker network create --subnet 172.30.1.0/24 frontend-net
docker network create --subnet 172.30.2.0/24 backend-net
docker network ls --filter name=-net
```

## Demonstration

Start a "database" on the backend network and an "API" on both networks (a container can be connected to several):

<!-- test: contains=api; output -->
```bash
docker run -d --name db --network backend-net nginx:1.30-alpine > /dev/null
docker run -d --name api --network frontend-net nginx:1.30-alpine > /dev/null
docker network connect backend-net api
docker inspect api --format '{{range $name, $net := .NetworkSettings.Networks}}api on {{$name}}: {{$net.IPAddress}}{{"\n"}}{{end}}'
```

```text
api on backend-net: 172.30.2.3
api on frontend-net: 172.30.1.2
```

The API reaches the database by name; a proxy on the frontend network only reaches the API:

<!-- test: contains=api -> db: ok; contains=proxy -> api: ok; output; retry=5 -->
```bash
docker exec api wget -qO /dev/null -T 3 http://db && echo "api -> db: ok"
docker run --rm --network frontend-net busybox:1.37 wget -qO /dev/null -T 3 http://api && echo "proxy -> api: ok"
```

```text
api -> db: ok
proxy -> api: ok
```

## Command breakdown

| Command | What it does |
|---|---|
| `docker network create [--subnet CIDR] NAME` | create a user-defined bridge network |
| `docker run --network NAME` | start a container on that network |
| `docker network connect NET CONTAINER` | add a running container to another network (a new interface) |
| `docker network disconnect NET CONTAINER` | remove it from that network |
| `docker network inspect NAME` | subnet, gateway and attached containers |
| `docker network rm NAME` | delete a network (no containers may be attached) |

## Hands-on lab

**Instructions.** Show the subnet and gateway of `backend-net`, and the names of the containers attached to it.

**Expected result.** Subnet `172.30.2.0/24`, a gateway in it, and the containers `db` and `api`.

**Verification.**

<!-- test: contains=172.30.2.0/24; contains=db; contains=api -->
```bash
docker network inspect backend-net --format '{{(index .IPAM.Config 0).Subnet}} via {{(index .IPAM.Config 0).Gateway}}'
docker network inspect backend-net --format '{{range .Containers}}{{.Name}} {{end}}'
```

## Break it

The proxy tries to reach the database directly:

<!-- test: fail; contains=bad address; output -->
```bash
docker run --rm --network frontend-net busybox:1.37 wget -qO /dev/null -T 3 http://db 2>&1
```

```text
wget: bad address 'db'
```

## Troubleshoot it

`bad address 'db'`: Docker's DNS only answers names of containers **on the same network** as the one asking. Check
which networks each container is on:

<!-- test: contains=db: backend-net; output -->
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

## Practice challenge

Create a network `lab-net` with the subnet `10.10.0.0/24` and start a container on it with the fixed address
`10.10.0.50`. Prove the address from inside the container.

<details>
<summary>Solution</summary>

<!-- test: contains=10.10.0.50; output -->
```bash
docker network create --subnet 10.10.0.0/24 lab-net > /dev/null
docker run --rm --network lab-net --ip 10.10.0.50 alpine:3.23 sh -c "ip -4 -o addr show eth0 | awk '{print \$4}'"
docker network rm lab-net > /dev/null
```

```text
10.10.0.50/24
```

`--ip` only works on user-defined networks with a subnet you configured. Use it sparingly: names are better than
addresses.

</details>

## Real-world example

A web shop runs a reverse proxy, an API and a database. The proxy and the API share a `frontend` network; the API and
the database share a `backend` network. If the proxy is ever compromised, the attacker cannot even resolve the
database's name. Docker Compose sets this up with a `networks:` key per service (lesson 065).

## Recap

- `docker network create` makes a user-defined bridge with DNS, isolation and a subnet you can choose.
- Containers resolve each other's names only on networks they share.
- `docker network connect`/`disconnect` changes a running container's networks.
- Split networks by tier (frontend, backend) so each container reaches only what it needs.

## Cleanup

<!-- test -->
```bash
docker rm -f db api worker > /dev/null
docker network rm frontend-net backend-net > /dev/null
```

Next: [Lesson 049 · Container-to-container communication](../049-container-to-container/README.md)
