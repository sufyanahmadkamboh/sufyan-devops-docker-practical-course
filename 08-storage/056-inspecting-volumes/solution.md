<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 056 · Inspecting volumes · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Find out how much disk space all your volumes use, and which volume is the largest, using `docker system df -v`.

## Solution

```bash
docker system df -v | grep -A6 '^Local Volumes space usage:'
```

```text
Local Volumes space usage:

VOLUME NAME                                                        LINKS     SIZE
a20fecfb516f4dbc6667963aa462ef1868e56c6b29276fe0ab1d3dfd0b22d985   0         17B
journal-data                                                       0         34B
b4ae83cca42c7bfc1db1b6a9889e8f1acbb0a33cad406e4d3b762ae78fccdb15   0         17B
orders                                                             0         0B
```

The `SIZE` column shows each volume's size and `LINKS` how many containers use it (0 = dangling).
