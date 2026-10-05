<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 046 · Networking fundamentals · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show the IPv4 address and the default gateway of a container on the default `bridge` network, and
the subnet of that network as Docker reports it.

**Expected result.** The address is inside the subnet, and the gateway is the subnet's first address (for example
`172.17.0.2`, gateway `172.17.0.1`, subnet `172.17.0.0/16`; the numbers can differ on your engine).

**Verification.**

```bash
docker run --rm alpine:3.23 sh -c "ip -4 -o addr show eth0 | awk '{print \"address\", \$4}'; ip route | awk '/default/ {print \"gateway\", \$3}'"
docker network inspect bridge --format 'subnet {{(index .IPAM.Config 0).Subnet}}'
```
