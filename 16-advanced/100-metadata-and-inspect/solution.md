<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 100 · Metadata and docker inspect · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Audit the host: for every running container, print its name, user, whether it is privileged, its memory limit and
whether its root file system is read-only, one line each (lessons 080–086).

## Solution

```bash
docker ps -q | xargs docker inspect --format \
  '{{.Name}} user={{if .Config.User}}{{.Config.User}}{{else}}root{{end}} privileged={{.HostConfig.Privileged}} memory={{.HostConfig.Memory}} readonly={{.HostConfig.ReadonlyRootfs}}'
```

```text
/web user=root privileged=false memory=134217728 readonly=false
```

`{{if}}…{{else}}…{{end}}` handles the empty `User` field (empty means the image's default, root for nginx). Run on a
real host, this one line shows which containers ignore the security lessons.
