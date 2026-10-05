<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 019 · Listing and removing images · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-019 examples/site
cd ~/docker-practice/lesson-019
printf 'FROM nginx:1.30-alpine\nCOPY . /usr/share/nginx/html/\n' > Dockerfile
ls
```

## Demonstration

```bash
docker build -q -t cafe-site:1.0 . > /dev/null
echo "<p>New: oat milk.</p>" >> index.html
docker build -q -t cafe-site:1.1 . > /dev/null
docker image ls --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}' cafe-site
```

```bash
docker image ls --filter reference='python'                    # one repository
docker image ls --filter reference='*:*-alpine' --format '{{.Repository}}:{{.Tag}}'   # a name pattern
docker image ls --filter before=cafe-site:1.1 --format '{{.Repository}}:{{.Tag}}' cafe-site
docker image ls -q cafe-site                                   # only IDs, for scripts
```

```bash
echo "<p>Draft: new opening hours.</p>" >> index.html
docker build -q . > /dev/null
docker image ls --filter dangling=true --format '{{.Repository}}:{{.Tag}}  {{.ID}}'
```

```bash
docker image prune -f
```

## Hands-on lab

```bash
docker image rm cafe-site:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-site
```

## Break it

```bash
docker run -d --name cafe-site cafe-site:1.1 > /dev/null
docker stop cafe-site > /dev/null
docker image rm cafe-site:1.1
```

## Troubleshoot it

```bash
docker container ls -a --filter ancestor=cafe-site:1.1 --format '{{.Names}}  {{.Status}}'
```

## Fix it

```bash
docker rm cafe-site
docker image rm cafe-site:1.1
```

## Practice challenge

```bash
docker image tag alpine:3.23 cafe-base:1
docker image tag alpine:3.23 cafe-base:1.0
docker image rm cafe-base:1
docker image rm cafe-base:1.0
docker image ls --format '{{.Repository}}:{{.Tag}}' alpine
```

## Cleanup

```bash
docker image prune -f > /dev/null
rm -rf ~/docker-practice/lesson-019
```
