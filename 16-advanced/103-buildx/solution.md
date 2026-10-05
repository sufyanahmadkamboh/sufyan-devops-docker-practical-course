<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 103 · BuildKit and buildx · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Export the complete file system of the final `image` stage as a tar file with `--output type=tar`, and list the files
it contains. How many files does the runnable image have?

## Solution

```bash
docker buildx build -q --output type=tar,dest=image.tar . > /dev/null
tar -tf image.tar | grep -v '/$' | wc -l
tar -tf image.tar | grep -E 'go-api|passwd'
```

```text
1335
etc/passwd
go-api
```

The final image is the distroless base (CA certificates, time zone data, `/etc/passwd` with a `nonroot` user, but no
shell, no package manager and no other programs) plus one binary: very little for an attacker to use (lesson 080).
