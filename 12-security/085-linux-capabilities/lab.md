<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 085 · Linux capabilities · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start a container with `--cap-drop ALL --cap-add CHOWN` and show with `caps.sh` that it has exactly
one capability, then show that `chown` works again.

**Expected result.** `CapEff=…: CHOWN` and `chown ok`.

**Verification.**

```bash
docker run --rm --cap-drop ALL --cap-add CHOWN -v "$(pwd)/caps.sh:/caps.sh:ro" alpine:3.23 \
  sh -c 'sh /caps.sh; touch /tmp/f && chown nobody /tmp/f && echo "chown ok"'
```
