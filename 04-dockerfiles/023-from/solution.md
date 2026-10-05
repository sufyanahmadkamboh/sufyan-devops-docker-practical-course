<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 023 · FROM: choosing a base image · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Alpine uses the `musl` C library, Debian `glibc`; a program compiled for one may not run on the other. Find the dynamic
loader of each base under `/lib` to see which C library it uses.

## Solution

```bash
docker run --rm alpine:3.23 sh -c 'ls /lib | grep "^ld-"'
docker run --rm debian:13-slim sh -c 'ls /lib64 /lib/x86_64-linux-gnu 2>/dev/null | grep "^ld-" | head -1'
```

```text
ld-musl-x86_64.so.1
ld-linux-x86-64.so.2
```

`ld-musl…` is musl, `ld-linux…` is glibc. Pre-compiled binaries (some Python wheels, Node.js native modules,
vendor tools) are often built for glibc only: on Alpine they fail with confusing "not found" errors, although the file
exists. That is a common reason to choose a `-slim` (Debian) base instead of `-alpine`. (On an ARM computer the names
end in `aarch64`.)
