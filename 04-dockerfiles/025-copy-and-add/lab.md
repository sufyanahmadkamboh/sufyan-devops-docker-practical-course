<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 025 · COPY and ADD · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Build an image whose `/usr/share/nginx/html/` contains the files of `public/`, based on
`nginx:1.30-alpine`, run it on port 8080 and fetch the page.

**Expected result.** `curl` returns the cafe's page.

**Verification.**

```bash
cd ~/docker-practice/lesson-025/menu-service
printf 'FROM nginx:1.30-alpine\nCOPY public/ /usr/share/nginx/html/\n' > Dockerfile.site
docker build -q -f Dockerfile.site -t copy-demo:site . > /dev/null
docker run -d --name copy-site -p 8080:80 copy-demo:site > /dev/null && echo "started"
```

```bash
curl -s http://localhost:8080
```
