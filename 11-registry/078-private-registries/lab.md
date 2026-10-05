<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 078 · Private registries · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Log out of the private registry and check that its entry has disappeared from `config.json`.

**Expected result.** `Removing login credentials for localhost:5001`, and no `localhost:5001` in the file.

**Verification.**

```bash
docker logout localhost:5001
grep -c '"localhost:5001":' ~/.docker/config.json || true
```
