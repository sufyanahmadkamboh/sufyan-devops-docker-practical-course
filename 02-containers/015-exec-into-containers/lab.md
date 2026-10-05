<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 015 · Running commands in containers (exec) · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** With one `docker exec`, replace the default page of `web` with `<h1>Changed with exec</h1>`, then
fetch it from your computer.

**Expected result.** `Changed with exec` from <http://localhost:8080>.

**Verification.**

```bash
docker exec web sh -c 'echo "<h1>Changed with exec</h1>" > /usr/share/nginx/html/index.html'
curl -s http://localhost:8080
```

Without `sh -c`, the `>` would be interpreted by **your** shell and write a file on your computer.
