<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 045 · Comparing the stacks · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

For the Go image, the program is about 8 MB (lesson 042). How many percent of the image's files are the program
itself? Measure both with `du` inside a container (`du -sk FILE` prints kilobytes; `-x` stays on one file system, so
`/proc` and `/sys` are not counted).

## Solution

```bash
binary=$(docker run --rm stack-go-api:1.0 du -sk /usr/local/bin/go-api | cut -f1)
total=$(docker run --rm stack-go-api:1.0 du -skx / 2> /dev/null | cut -f1)
echo "program: $binary kB of $total kB = $((binary * 100 / total)) % of the image"
```

```text
program: 8424 kB of 293808 kB = 2 % of the image
```

A few percent: the rest is the Go toolchain and Alpine, which the program never uses. Lesson 089 brings this image down
to little more than the binary.
