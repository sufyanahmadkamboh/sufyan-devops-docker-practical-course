<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 028 · ENTRYPOINT · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Look up the price of a cappuccino, then show the image's entrypoint with `docker image inspect`.

**Expected result.** `3.20 EUR` and `["price"]`.

**Verification.**

```bash
docker run --rm price:1.0 cappuccino
docker image inspect --format '{{json .Config.Entrypoint}}' price:1.0
```
