<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 012 · Port mapping · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A third website should also use port 8080:

```bash
docker run -d --name web-c -p 8080:80 nginx:1.30-alpine 2>&1
```

```text
0cf65dc51777bdd456a73b98f7ba33bd57b3cb74e3c1c96dfa377239ab3316f9
docker: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint web-c (f42c29704b02595cd49c52f5b25cb7fab4e474d7a349f92ec0001287c4201e70): Bind for 0.0.0.0:8080 failed: port is already allocated

Run 'docker run --help' for more information
```

## Troubleshoot it

`Bind for 0.0.0.0:8080 failed: port is already allocated`: one host port, one listener. Docker created the container
(it is in `docker ps -a` as `Created`) but could not start it. Find out who owns the port. If it is another container,
`docker ps` shows it:

```bash
docker ps --filter publish=8080 --format '{{.Names}} owns {{.Ports}}'
```

```text
web-a owns 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

If no container owns it, another program on your computer does: `ss -ltnp | grep 8080` on Linux, `lsof -i :8080` on
macOS, `netstat -ano | findstr 8080` on Windows. Then the error reads `address already in use` (troubleshooting
problem 04).

## Fix it

Remove the half-created container and use a free host port:

<!-- test: contains=80/tcp -> 0.0.0.0:8083 -->
```bash
docker rm web-c > /dev/null
docker run -d --name web-c -p 8083:80 nginx:1.30-alpine > /dev/null
docker port web-c
```
