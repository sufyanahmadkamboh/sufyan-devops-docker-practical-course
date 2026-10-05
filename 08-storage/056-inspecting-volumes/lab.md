<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 056 · Inspecting volumes · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Show the creation date and the driver of `orders`, and list every container that uses the anonymous
volume of `journal-1`.

**Expected result.** A timestamp and `local`; the container `journal-1`.

**Verification.**

```bash
docker volume inspect orders --format '{{.CreatedAt}} {{.Driver}}'
docker ps -a --filter volume="$(docker inspect journal-1 --format '{{range .Mounts}}{{.Name}}{{end}}')" --format '{{.Names}}'
```
