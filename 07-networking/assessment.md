# Module 07 assessment · Networking

> Lessons [046](046-networking-fundamentals/README.md)–[052](052-network-troubleshooting/README.md) · ⏱ 40 minutes ·
> try every question before opening its answer

## Knowledge check

**1. What does every container get from its network namespace?**

<details><summary>Answer</summary>

Its own network interfaces, IP addresses, routing table and port space. Two containers can both listen on port 80
without a conflict (lesson 046).

</details>

**2. Two containers on the default `bridge` network: can they reach each other by container name?**

<details><summary>Answer</summary>

No. The default bridge has no DNS for container names; only IP addresses work, and those change when a container is
recreated. User-defined networks resolve names (lessons 047, 048).

</details>

**3. What is `127.0.0.11` inside a container?**

<details><summary>Answer</summary>

Docker's embedded DNS server on user-defined networks. It answers container names and network aliases of the same
network and forwards every other name (lesson 050).

</details>

**4. Does `EXPOSE 8080` in a Dockerfile make the application reachable from the host?**

<details><summary>Answer</summary>

No. `EXPOSE` is documentation. Only publishing with `-p HOST:CONTAINER` (or `-P`) forwards a host port (lesson 051).

</details>

**5. The API container must reach Redis in the same network. Which host and port does it use?**

<details><summary>Answer</summary>

The Redis container's name (or an alias) and the **container** port, `redis:6379`. Published host ports are only for
traffic from outside Docker (lesson 049).

</details>

**6. `curl localhost:8080` gives `Empty reply from server`, while `docker port` shows `8000/tcp -> 0.0.0.0:8080`. What
do you check next?**

<details><summary>Answer</summary>

What the application really listens on, inside its namespace:
`docker run --rm --network container:NAME busybox:1.37 netstat -tln`. Typical causes: it listens on `127.0.0.1`, or
on a different port than 8000 (lesson 052).

</details>

**7. Does `--hostname api` let other containers reach the container as `api`?**

<details><summary>Answer</summary>

No. It only sets the name the container sees for itself. Use the container name or `--network-alias api`
(lesson 050).

</details>

**8. Why publish a development database with `-p 127.0.0.1:5432:5432` instead of `-p 5432:5432`?**

<details><summary>Answer</summary>

`-p 5432:5432` listens on every interface of the host, so other machines on the network (or the internet, on a cloud
VM) can connect. `127.0.0.1:` limits it to the local computer (lesson 051).

</details>

## Practical task

Create a network `exam-net`. Run nginx as `menu` on it **without** publishing any port, prove that a client container
reaches it by name, then run a second nginx `menu-public` published only on `127.0.0.1:8090` and fetch it from your
computer.

<details><summary>Solution</summary>

<!-- test: contains=by name: ok; contains=Welcome to nginx; contains=127.0.0.1:8090; output; retry=5 -->
```bash
docker network create exam-net > /dev/null
docker run -d --name menu --network exam-net nginx:1.30-alpine > /dev/null
docker run -d --name menu-public -p 127.0.0.1:8090:80 nginx:1.30-alpine > /dev/null
sleep 1
docker run --rm --network exam-net busybox:1.37 wget -qO /dev/null -T 5 http://menu && echo "by name: ok"
docker port menu-public
curl -s http://127.0.0.1:8090 | grep -o '<title>.*</title>'
```

```text
by name: ok
80/tcp -> 127.0.0.1:8090
<title>Welcome to nginx!</title>
```

</details>

## Troubleshooting task

Set up the broken system: an orders service and a client that cannot reach it.

<!-- test: fail; contains=bad address -->
```bash
docker network create orders-net > /dev/null
docker network create client-net > /dev/null
docker run -d --name orders --network orders-net python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
docker run -d --name client --network client-net alpine:3.23 sleep 600 > /dev/null
docker exec client wget -qO /dev/null -T 5 http://orders 2>&1
```

Find **every** problem (there are two), fix them without recreating `orders`, and prove the client gets an answer.

<details><summary>Solution</summary>

Problem 1, `bad address 'orders'`: the containers share no network, so the name does not resolve. Problem 2, revealed
once the name resolves: the client calls port 80, but `orders` listens on 8000:

<!-- test: contains=orders-net; contains=0.0.0.0:8000; contains=client -> orders: ok; output; retry=5 -->
```bash
docker inspect client --format '{{range $n, $_ := .NetworkSettings.Networks}}client on {{$n}}{{end}}'
docker inspect orders --format '{{range $n, $_ := .NetworkSettings.Networks}}orders on {{$n}}{{end}}'
docker network connect orders-net client
docker exec client wget -qO /dev/null -T 5 http://orders 2>&1 || true
docker run --rm --network container:orders busybox:1.37 netstat -tln | grep 8000
docker exec client wget -qO /dev/null -T 5 http://orders:8000 && echo "client -> orders: ok"
```

```text
client on client-net
orders on orders-net
wget: can't connect to remote host (172.19.0.2): Connection refused
tcp        0      0 0.0.0.0:8000            0.0.0.0:*               LISTEN      
client -> orders: ok
```

</details>

## Real-world scenario

Your team runs a reverse proxy, an API and a Postgres database with plain `docker run` on one server, all on the
default bridge network, configured with IP addresses. Postgres is published with `-p 5432:5432` "so we can debug it".
After a reboot the API cannot reach the database. What is wrong with this setup, and what would you change?

<details><summary>Model answer</summary>

IP addresses on the default bridge are not stable: after the reboot the containers came back in another order with
different addresses (lesson 047). Create user-defined networks and use names: `frontend` (proxy, API) and `backend`
(API, Postgres), so the proxy cannot even resolve the database (lesson 048). Configure the API with `DB_HOST=postgres`
(lesson 049). Remove `-p 5432:5432`: it exposes the database on every interface of the server; for debugging use
`docker exec` or `-p 127.0.0.1:5432:5432` (lesson 051). Docker Compose creates this structure from one file
(lesson 065).

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f menu menu-public orders client > /dev/null
docker network rm exam-net orders-net client-net > /dev/null
```
