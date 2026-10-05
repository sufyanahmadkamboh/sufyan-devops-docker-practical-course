<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 017 · Image layers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

`layers-demo:fixed` and `alpine:3.23` should share their base layer. Prove it by comparing the first layer digest of
both images.

## Solution

```bash
a=$(docker image inspect --format '{{index .RootFS.Layers 0}}' alpine:3.23)
b=$(docker image inspect --format '{{index .RootFS.Layers 0}}' layers-demo:fixed)
echo "alpine: $a"
echo "fixed:  $b"
[ "$a" = "$b" ] && echo "shared base layer: stored once on disk"
```

```text
alpine: sha256:e63b02c2b5c761df2cb95e657d744f27d95da4e051235a13c80b88cd68eab188
fixed:  sha256:e63b02c2b5c761df2cb95e657d744f27d95da4e051235a13c80b88cd68eab188
shared base layer: stored once on disk
```

`index LIST 0` takes the first entry: the base layer. Same content, same digest, one copy on disk; a registry also
stores it once and a pull skips layers that are already present.
