<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 047 · The default bridge network · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Find the gateway address of the default bridge network, and show that `web` answers on its IP from a
second container.

**Expected result.** A gateway such as `172.17.0.1`, and nginx's welcome page title.

**Verification.**

```bash
docker network inspect bridge --format 'gateway {{(index .IPAM.Config 0).Gateway}}'
docker run --rm busybox:1.37 wget -qO- "http://$(docker inspect web --format '{{.NetworkSettings.Networks.bridge.IPAddress}}')" | grep -o '<title>.*</title>'
```
