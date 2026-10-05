<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 096 · docker events · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Create a network and a volume, remove both, and list the events of type `network` and `volume` from
the last minute.

**Expected result.** `network create`, `network destroy`, `volume create`, `volume destroy` (in time order).

**Verification.**

```bash
docker network create lab-net > /dev/null && docker network rm lab-net > /dev/null
docker volume create lab-vol > /dev/null && docker volume rm lab-vol > /dev/null
sleep 1
docker events --since 1m --until "$(date +%s)" --filter type=network --filter type=volume --format '{{.Type}} {{.Action}}'
```
