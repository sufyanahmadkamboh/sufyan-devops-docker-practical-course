<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 104 · Multi-architecture images · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A colleague needs the image on a Raspberry Pi with a 32-bit operating system (`linux/arm/v7`):

```bash
docker run --rm --platform linux/arm/v7 cafe-hello:1.0 2>&1
```

```text
Unable to find image 'cafe-hello:1.0' locally
docker: Error response from daemon: pull access denied for cafe-hello, repository does not exist or may require 'docker login'

Run 'docker run --help' for more information
```

## Troubleshoot it

The image index has no `arm/v7` variant. Docker found the tag locally, but nothing for that platform, so it tried to
pull it from Docker Hub, where `cafe-hello` does not exist (`pull access denied`). List what the tag contains:

```bash
docker image ls --tree cafe-hello
```

```text
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
cafe-hello:1.0       ece6197c65c4       7.54MB         2.79MB        
├─ linux/amd64       68f2b68e502b       3.86MB         1.44MB        
└─ linux/arm64       42bc0ea73444       3.68MB         1.34MB        

cafe-hello:arm       dca66b67445a       3.68MB         1.34MB        
└─ linux/arm64       42bc0ea73444       3.68MB         1.34MB        
```

Other errors of this family and their causes:

| Message | Cause |
|---|---|
| `exec format error` | a binary for another architecture without emulation (QEMU/binfmt not installed on that Linux host) |
| `docker exporter does not currently support exporting manifest lists` | `--load` of several platforms on the classic image store: push to a registry instead, or enable the containerd image store |
| `no match for platform in manifest` | pulling an image that was published for other platforms only |

## Fix it

Add the platform to the build. Go cross-compiles for it, and `scratch` needs no base image, so nothing new is
downloaded:

```bash
docker buildx build -q --platform linux/amd64,linux/arm64,linux/arm/v7 -t cafe-hello:1.0 --load . > /dev/null
docker image ls --tree cafe-hello
```

```text
IMAGE                 ID             DISK USAGE   CONTENT SIZE   EXTRA
cafe-hello:1.0        6edd47fa2b03       8.88MB         4.12MB        
├─ linux/amd64        68f2b68e502b       3.86MB         1.44MB        
├─ linux/arm64        42bc0ea73444       3.68MB         1.34MB        
└─ linux/arm/v7       5b50b1c416e0       1.33MB         1.33MB        

cafe-hello:arm        dca66b67445a       3.68MB         1.34MB        
└─ linux/arm64        42bc0ea73444       3.68MB         1.34MB        
```

The Raspberry Pi now pulls the `arm/v7` variant and runs it natively. Running that variant **here** needs emulation for
32-bit ARM, which not every Docker installation has; without it you get `exec format error`, the first message of the
table above.
