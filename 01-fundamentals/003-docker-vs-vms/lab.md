<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 003 · Docker vs virtual machines · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Start an Ubuntu container and a BusyBox container, and show that both report the engine's kernel even
though Ubuntu and BusyBox are completely different user spaces.

**Expected result.** Both print the same kernel release as `docker info --format '{{.KernelVersion}}'`.

**Verification.**

```bash
[ "$(docker run --rm ubuntu:24.04 uname -r)" = "$(docker run --rm busybox:1.37 uname -r)" ] && echo "kernels match"
```
