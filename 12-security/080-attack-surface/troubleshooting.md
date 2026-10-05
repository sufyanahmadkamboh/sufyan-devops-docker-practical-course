<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 080 · The attack surface of a container · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate cannot get a tool to work in a container and "fixes" it with `--privileged`. Compare what a normal and a
privileged container can see and do:

```bash
echo "normal:     $(docker run --rm alpine:3.23 sh -c 'ls /dev | wc -l') devices, $(docker run --rm alpine:3.23 grep CapEff /proc/self/status)"
echo "privileged: $(docker run --rm --privileged alpine:3.23 sh -c 'ls /dev | wc -l') devices, $(docker run --rm --privileged alpine:3.23 grep CapEff /proc/self/status)"
```

```text
normal:     15 devices, CapEff:	00000000a80425fb
privileged: 174 devices, CapEff:	000001ffffffffff
```

## Troubleshoot it

The privileged container sees every device of the host (disks included) and has **every** capability (`CapEff` with
all bits set): with the host's disk device, it can mount the host's file system and change anything on it. The kernel
settings are writable too:

```bash
docker run --rm --privileged alpine:3.23 sysctl -w net.ipv4.ip_forward=1
```

```text
net.ipv4.ip_forward = 1
```

In lesson 003 the same command failed with `Read-only file system`. To find privileged containers on a host, ask
Docker:

```bash
docker run -d --name too-powerful --privileged alpine:3.23 sleep 300 > /dev/null
docker ps -q | xargs docker inspect --format '{{.Name}} Privileged={{.HostConfig.Privileged}}'
```

## Fix it

Remove `--privileged`. Find out which permission the tool actually needs and grant only that (a single capability with
`--cap-add`, lesson 085, or a single device with `--device`):

```bash
docker rm -f too-powerful > /dev/null
docker run -d --name just-enough alpine:3.23 sleep 300 > /dev/null
docker inspect --format '{{.Name}} Privileged={{.HostConfig.Privileged}}' just-enough
docker rm -f just-enough > /dev/null
```
