<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 005 · Installing Docker · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Print, on one line, the engine version, the storage driver and the logging driver of your engine.

**Expected result.** Three values, for example `29.4.3 overlayfs json-file` (versions and the storage driver differ
between installations).

**Verification.**

```bash
docker info --format '{{.ServerVersion}} {{.Driver}} {{.LoggingDriver}}'
```
