<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 133 · Production configuration · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The configuration is mounted read-only. Prove it: try to change the file from inside the container, and show the
error.

## Solution

```bash
docker exec web sh -c 'echo "# changed" >> /etc/nginx/conf.d/default.conf' 2>&1 || true
```

```text
sh: can't create /etc/nginx/conf.d/default.conf: Read-only file system
```

`:ro` makes the mount read-only inside the container: neither the application nor an attacker who gets into the
container can change its configuration. Changing it means changing the file on the host (or in Git) and restarting
the container.
