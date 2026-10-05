<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 047 · The default bridge network · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Use the container's name instead of its IP, as you would in an application's configuration:

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

```bash
docker run --rm busybox:1.37 cat /etc/resolv.conf | grep nameserver
```

```text
nameserver 192.168.65.7
```

On the default bridge, a container gets the host's DNS servers (on Docker Desktop, the VM's resolver), which know
public names but nothing about containers. Docker's own DNS server for container names only serves **user-defined**
networks. And the IP is not a reliable fallback: recreate `web` and it can get a different one:

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

```bash
docker network create shop-net > /dev/null
docker network connect shop-net web
docker run --rm --network shop-net busybox:1.37 wget -qO- http://web | grep -o '<title>.*</title>'
```

```text
<title>Welcome to nginx!</title>
```

The old `--link` option made names work on the default bridge; it is deprecated and should not be used any more.
