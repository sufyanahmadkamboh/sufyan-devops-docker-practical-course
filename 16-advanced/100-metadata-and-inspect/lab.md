<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 100 · Metadata and docker inspect · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** With one `docker inspect --format` command, print the container's restart policy, its memory limit
in bytes, and the host port of `80/tcp`.

**Expected result.** `restart=no memory=134217728 port=8080`.

**Verification.**

```bash
docker inspect --format 'restart={{.HostConfig.RestartPolicy.Name}} memory={{.HostConfig.Memory}} port={{(index (index .NetworkSettings.Ports "80/tcp") 0).HostPort}}' web
```
