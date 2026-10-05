<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 046 · Networking fundamentals · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A nightly job downloads a file. Someone hardened it by starting it with `--network none`:

```bash
docker run --rm --network none alpine:3.23 wget -q -T 5 -O /dev/null http://example.com 2>&1
```

```text
wget: bad address 'example.com'
```

## Troubleshoot it

`bad address 'example.com'`: the name could not be resolved, because the container has no network at all, not even a
DNS server to ask. The first question for any connection problem in a container is "which network is it on?":

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

```bash
docker run --rm alpine:3.23 sh -c 'wget -q -T 10 -O /dev/null http://example.com && echo downloaded'
```

`--network none` is still the right choice for jobs that only process local files: no network means nothing to attack
and nothing to leak.
