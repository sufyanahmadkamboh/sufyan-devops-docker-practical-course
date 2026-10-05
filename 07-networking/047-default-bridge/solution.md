<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 047 · The default bridge network · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

`web` is now on two networks. Show both of its IP addresses, one per network.

## Solution

```bash
docker inspect web --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{$net.IPAddress}}{{"\n"}}{{end}}'
```

```text
bridge 172.17.0.3
shop-net 172.18.0.2
```

A container gets one interface and one address per network it is connected to.
