<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 003 · Docker vs virtual machines · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Because the kernel is shared, a container must not be allowed to change kernel settings for everyone. Try it:

```bash
docker run --rm alpine:3.23 sysctl -w net.ipv4.ip_forward=0
```

```text
sysctl: error setting key 'net.ipv4.ip_forward': Read-only file system
```

## Troubleshoot it

`Read-only file system`: Docker mounts `/proc/sys` (the kernel's settings) read-only inside the container. In a VM you
own the kernel and could change it; in a container you would be changing the kernel of the host and every other
container on it. This is a security boundary, not a bug. Look at how `/proc/sys` is mounted:

```bash
docker run --rm alpine:3.23 sh -c 'grep " /proc/sys " /proc/mounts'
```

## Fix it

Some kernel settings are **namespaced**: each container has its own copy (most network settings are). Docker lets you
set those at start time, safely, with `--sysctl`:

```bash
docker run --rm --sysctl net.ipv4.ip_forward=1 alpine:3.23 sysctl net.ipv4.ip_forward
```

```text
net.ipv4.ip_forward = 1
```

Settings that are not namespaced (memory management, most of `kernel.*`) can only be changed on the host. If an
application truly needs its own kernel or kernel modules, it needs a VM, not a container.
