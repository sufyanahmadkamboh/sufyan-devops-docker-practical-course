<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 027 · CMD · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Run `menu:cmd` three times: with its default command, with `head -2 menu.csv`, and with
`grep cappuccino menu.csv`.

**Expected result.** The whole menu, the first two lines, and the cappuccino line.

**Verification.**

```bash
docker run --rm menu:cmd
docker run --rm menu:cmd head -2 menu.csv
docker run --rm menu:cmd grep cappuccino menu.csv
```
