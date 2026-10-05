<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 022 · Your first Dockerfile · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Change the heading of `index.html` to "Welcome to the cafe, version 1.1", build `cafe-site:1.1`,
and run it as `cafe-site-v11` on port 8081.

**Expected result.** `curl http://localhost:8081` shows the new heading; port 8080 still shows the old one.

**Verification.**

```bash
cd ~/docker-practice/lesson-022
sed -i.bak 's|Welcome to the cafe|Welcome to the cafe, version 1.1|' index.html && rm index.html.bak
docker build -q -t cafe-site:1.1 . > /dev/null
docker run -d --name cafe-site-v11 -p 8081:80 cafe-site:1.1 > /dev/null && echo "lab ready"
```

```bash
curl -s http://localhost:8081 | grep '<h1>'
curl -s http://localhost:8080 | grep '<h1>'
```

The running container of 1.0 did not change: an image is fixed once built.
