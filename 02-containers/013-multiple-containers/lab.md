<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 013 · Running multiple containers · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Add a third website `site-c` on port 8082 with the content `Site c`, with the same label, and show
that the group now has four containers.

**Expected result.** `Site c` from port 8082, and `4` containers with the label.

**Verification.**

```bash
docker run -d --name site-c --label project=lesson-013 -p 8082:80 nginx:1.30-alpine \
  sh -c "echo '<h1>Site c</h1>' > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"
```

```bash
curl -s http://localhost:8082
docker ps -q --filter label=project=lesson-013 | wc -l | tr -d ' '
```
