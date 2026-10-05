<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 104 · Multi-architecture images · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Prove that the build stage ran on the build machine's own platform and was **not** emulated: add a temporary `RUN`
step that prints `$BUILDPLATFORM`, `$TARGETPLATFORM` and `uname -m` in the build stage, and build for `linux/arm64`
with plain progress output.

## Solution

```bash
awk '/^RUN CGO_ENABLED/ {
  print "ARG BUILDPLATFORM TARGETPLATFORM"
  print "RUN echo \"BUILDPLATFORM=$BUILDPLATFORM TARGETPLATFORM=$TARGETPLATFORM uname=$(uname -m)\""
} { print }' Dockerfile > Dockerfile.debug
docker buildx build --no-cache --progress plain --platform linux/arm64 -f Dockerfile.debug -t cafe-hello:debug . 2>&1 |
  grep -o 'BUILDPLATFORM=.*uname=[a-z0-9_]*$' | head -1
```

```text
BUILDPLATFORM=linux/amd64 TARGETPLATFORM=linux/arm64 uname=x86_64
```

The build stage reports the machine's own architecture (`x86_64` here; `aarch64` on an ARM machine) while building for
`linux/arm64`: the Go compiler did the cross-compilation, natively and quickly.
