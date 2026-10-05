<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 034 · Dockerfile best practices · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Without touching the `COPY . /app` line, make `Dockerfile.before` pass `docker build --check` and keep the `notes/`
folder and the Dockerfiles out of its image.

## Solution

```bash
cd ~/docker-practice/lesson-034
sed -i.bak 's/^CMD node server.js$/CMD ["node", "server.js"]/' Dockerfile.before && rm Dockerfile.before.bak
printf 'notes/\nDockerfile*\nnode_modules\n' > Dockerfile.before.dockerignore
docker build --check -f Dockerfile.before . 2>&1 | tail -1
docker build -q -f Dockerfile.before -t cafe-api:before . > /dev/null
echo "files in /app: $(docker run --rm cafe-api:before ls -A /app | tr '\n' ' ')"
```

```text
Check complete, no warnings found.
files in /app: package-lock.json package.json server.js 
```

The exec form satisfies the check; an ignore file named after the Dockerfile shrinks the build context, so `COPY .`
no longer sees the notes. The image still runs as root and re-installs dependencies on every code change: the checker
does not know your intentions, which is why the review checklist matters.
