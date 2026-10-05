<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 033 · USER · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build `Dockerfile.fixed` as `orders:1.0`, take an order for a cappuccino, and check who owns the order
log.

**Expected result.** The log shows the order; the file belongs to `appuser`.

**Verification.**

```bash
cd ~/docker-practice/lesson-033
docker build -q -f Dockerfile.fixed -t orders:1.0 . > /dev/null
docker run --rm orders:1.0 cappuccino
docker run --rm --entrypoint sh orders:1.0 -c './take-order.sh latte > /dev/null; ls -l /app/data'
```
