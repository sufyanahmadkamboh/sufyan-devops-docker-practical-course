<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 048 · Custom networks · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Create a network `lab-net` with the subnet `10.10.0.0/24` and start a container on it with the fixed address
`10.10.0.50`. Prove the address from inside the container.

## Solution

```bash
docker network create --subnet 10.10.0.0/24 lab-net > /dev/null
docker run --rm --network lab-net --ip 10.10.0.50 alpine:3.23 sh -c "ip -4 -o addr show eth0 | awk '{print \$4}'"
docker network rm lab-net > /dev/null
```

```text
10.10.0.50/24
```

`--ip` only works on user-defined networks with a subnet you configured. Use it sparingly: names are better than
addresses.
