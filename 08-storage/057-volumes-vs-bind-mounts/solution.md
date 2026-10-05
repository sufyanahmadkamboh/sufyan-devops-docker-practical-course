<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 057 · Volumes vs bind mounts · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Give a container a 16 MB in-memory scratch directory at `/scratch`, prove that it is a `tmpfs`, and show that its
content is gone after a restart.

## Solution

```bash
docker run -d --name scratch --mount type=tmpfs,target=/scratch,tmpfs-size=16m alpine:3.23 sleep 300 > /dev/null
docker exec scratch sh -c 'grep " /scratch " /proc/mounts; echo temp > /scratch/file.txt'
docker restart scratch > /dev/null
echo "after restart: [$(docker exec scratch ls /scratch)]"
```

```text
tmpfs /scratch tmpfs rw,nosuid,nodev,noexec,relatime,size=16384k 0 0
after restart: []
```

tmpfs data never touches the disk, which also makes it a good place for decrypted secrets and temporary files.
