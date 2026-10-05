<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 102 · Logging drivers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

To "save disk space", a teammate switches a service's logging off:

```bash
docker run -d --name quiet --log-driver none nginx:1.30-alpine > /dev/null && echo "started quiet"
```

Later, the service misbehaves:

```bash
docker logs quiet 2>&1
```

```text
Error response from daemon: configured logging driver does not support reading
```

## Troubleshoot it

`configured logging driver does not support reading`: the error names the cause. Check the driver:

```bash
docker inspect --format '{{.HostConfig.LogConfig.Type}}' quiet
```

```text
none
```

With `none`, every line the container wrote is gone; nothing can recover it. With a remote driver, the lines would be
in the remote system instead.

## Fix it

Never use `none` to save space: rotate instead. The logging driver cannot be changed on an existing container, so
recreate it:

```bash
docker rm -f quiet > /dev/null
docker run -d --name quiet --log-driver local --log-opt max-size=10m --log-opt max-file=3 nginx:1.30-alpine > /dev/null
docker inspect --format '{{.HostConfig.LogConfig.Type}} {{json .HostConfig.LogConfig.Config}}' quiet
```

```bash
docker logs quiet 2>&1 | grep 'Configuration complete'
```

For the whole engine, set the default in `daemon.json` (Docker Desktop: Settings → Docker Engine; Linux:
`/etc/docker/daemon.json`, then `sudo systemctl restart docker`):

```bash
{
  "log-driver": "local",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```
