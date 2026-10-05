# Lesson 102 · Logging drivers

> Level 17 · Advanced Docker · ⏱ 20 minutes · run every command from the course folder

## What are we learning?

Where container output goes is decided by the **logging driver**. The default, `json-file`, writes one JSON line per
log line into a file on the Docker host, **without size limit** unless you configure one: a chatty container can fill
the host's disk. Other drivers keep logs in a compact local format (`local`), send them to the system journal
(`journald`), to syslog, or to a central service (`fluentd`, `gelf`, `awslogs`, `gcplogs`, …), or discard them
(`none`). Some of them cannot be read back with `docker logs`.

## Visual

```text
  container stdout/stderr ──▶ logging driver ──┬─ json-file  file on the host (default; rotate with max-size/max-file)
                                               ├─ local      compact files, rotated by default        docker logs ✓
                                               ├─ journald   systemd journal                           docker logs ✓
                                               ├─ syslog / fluentd / gelf / awslogs / …  sent away      docker logs ✓*
                                               └─ none       discarded                                 docker logs ✗

  * since Docker 20.10, "dual logging" keeps a local copy so docker logs still works for remote drivers
```

## Lab setup

No files are needed: this lesson uses `alpine` and `nginx` containers.

## Demonstration

The engine's default driver:

<!-- test: contains=json-file; output -->
```bash
docker info --format 'default logging driver: {{.LoggingDriver}}'
```

```text
default logging driver: json-file
```

Each container records its driver and options in its configuration:

<!-- test: contains=json-file; output -->
```bash
docker run -d --name chatty alpine:3.23 sh -c 'pad=$(printf "%0100d" 0); i=0; while [ $i -lt 50000 ]; do i=$((i+1)); echo "line $i $pad"; done; sleep 300' > /dev/null
docker inspect --format '{{.HostConfig.LogConfig.Type}} {{json .HostConfig.LogConfig.Config}}' chatty
```

```text
json-file {}
```

`chatty` writes 50,000 lines of about 110 characters as fast as it can. Without rotation, all of them stay in its log
file, and a long-running chatty service only ever adds to it (the file lives in the Docker host's file system, inside
the VM on Docker Desktop):

<!-- test: contains=lines so far; output -->
```bash
sleep 3
echo "$(docker logs chatty 2>&1 | wc -l) lines so far"
docker inspect --format '{{.LogPath}}' chatty
```

```text
50000 lines so far
/var/lib/docker/containers/c57ad811fc3fe59d760ffea486c039c979da31c6687bf6e1cbdbb418e0537777/c57ad811fc3fe59d760ffea486c039c979da31c6687bf6e1cbdbb418e0537777-json.log
```

## Command breakdown

| Option | What it does |
|---|---|
| `--log-driver NAME` | the driver for this container (`json-file`, `local`, `journald`, `none`, …) |
| `--log-opt max-size=10m` | rotate the file at 10 MB (json-file, local) |
| `--log-opt max-file=3` | keep 3 files: at most 30 MB per container with the line above |
| `--log-opt tag=…` | a tag for remote drivers (e.g. `{{.Name}}`) |
| `daemon.json` `"log-driver"`, `"log-opts"` | the engine-wide default (restart the engine; applies to new containers) |
| `docker inspect --format '{{.HostConfig.LogConfig}}'` | a container's driver and options |

## Hands-on lab

**Instructions.** Start a second chatty container with rotation: at most 3 files of 1 MB. Wait a few seconds and
show that `docker logs` holds only the most recent lines, while the unrotated `chatty` kept all 50,000.

**Expected result.** `rotated` keeps fewer lines (the oldest were rotated away, so its first line is not `line 1`);
`chatty` keeps 50,000.

**Verification.**

<!-- test: contains=rotated:; contains=chatty: -->
```bash
docker run -d --name rotated --log-opt max-size=1m --log-opt max-file=3 alpine:3.23 \
  sh -c 'pad=$(printf "%0100d" 0); i=0; while [ $i -lt 50000 ]; do i=$((i+1)); echo "line $i $pad"; done; sleep 300' > /dev/null
sleep 5
echo "rotated: $(docker logs rotated 2>&1 | wc -l) lines kept (first kept: $(docker logs rotated 2>&1 | head -1))"
echo "chatty:  $(docker logs chatty 2>&1 | wc -l) lines kept"
docker inspect --format '{{json .HostConfig.LogConfig.Config}}' rotated
```

## Break it

To "save disk space", a teammate switches a service's logging off:

<!-- test: contains=started quiet -->
```bash
docker run -d --name quiet --log-driver none nginx:1.30-alpine > /dev/null && echo "started quiet"
```

Later, the service misbehaves:

<!-- test: fail; contains=does not support reading; output -->
```bash
docker logs quiet 2>&1
```

```text
Error response from daemon: configured logging driver does not support reading
```

## Troubleshoot it

`configured logging driver does not support reading`: the error names the cause. Check the driver:

<!-- test: contains=none; output -->
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

<!-- test: contains=local {"max-file":"3","max-size":"10m"} -->
```bash
docker rm -f quiet > /dev/null
docker run -d --name quiet --log-driver local --log-opt max-size=10m --log-opt max-file=3 nginx:1.30-alpine > /dev/null
docker inspect --format '{{.HostConfig.LogConfig.Type}} {{json .HostConfig.LogConfig.Config}}' quiet
```

<!-- test: retry=5; contains=Configuration complete -->
```bash
docker logs quiet 2>&1 | grep 'Configuration complete'
```

For the whole engine, set the default in `daemon.json` (Docker Desktop: Settings → Docker Engine; Linux:
`/etc/docker/daemon.json`, then `sudo systemctl restart docker`):

<!-- test: skip -->
```bash
{
  "log-driver": "local",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
```

## Practice challenge

Print a table of every running container with its logging driver and its `max-size` option, showing `unlimited` when
there is none.

<details>
<summary>Solution</summary>

<!-- test: contains=/chatty json-file unlimited; contains=/rotated json-file 1m; output -->
```bash
docker ps -q | xargs docker inspect --format \
  '{{.Name}} {{.HostConfig.LogConfig.Type}} {{with index .HostConfig.LogConfig.Config "max-size"}}{{.}}{{else}}unlimited{{end}}'
```

```text
/quiet local 10m
/rotated json-file 1m
/chatty json-file unlimited
```

`{{with X}}…{{else}}…{{end}}` prints the value when it exists and is not empty, and the fallback otherwise.

</details>

## Real-world example

A team's build server ran out of disk on a weekend: one container in a crash loop had written gigabytes of stack
traces into its `json-file` log. The fix was an engine-wide default of `local` with `max-size` and `max-file` in
`daemon.json`, plus shipping logs to a central system (Loki via the Grafana Agent, or the cloud provider's agent) where
they are retained by policy rather than by the size of a host's disk.

## Recap

- The logging driver decides where stdout/stderr go; the default is `json-file`, unrotated.
- Rotate with `--log-opt max-size=… --log-opt max-file=…`, or use the `local` driver; set defaults in `daemon.json`.
- `none` discards logs: `docker logs` fails with `does not support reading`, and the lines are lost.
- The driver is fixed when the container is created: recreate the container to change it.

## Cleanup

<!-- test -->
```bash
docker rm -f chatty rotated quiet > /dev/null 2>&1 || true
```

Next: [Lesson 103 · BuildKit and buildx](../103-buildx/README.md)
