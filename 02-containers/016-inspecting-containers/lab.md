<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 016 · Inspecting containers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Print, in one line, the name of `web`, its image, the host port bound to its port 80 and its restart
policy.

**Expected result.** `/web nginx:1.30-alpine 8080 unless-stopped`.

**Verification.**

```bash
docker inspect --format '{{.Name}} {{.Config.Image}} {{(index (index .HostConfig.PortBindings "80/tcp") 0).HostPort}} {{.HostConfig.RestartPolicy.Name}}' web
```

`index MAP "KEY"` reads a key that contains characters like `/`; `index LIST 0` reads the first entry.
