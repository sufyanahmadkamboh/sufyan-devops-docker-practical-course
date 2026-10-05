<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 053 · The container's writable layer · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Demonstration

```bash
docker run --name notes alpine:3.23 sh -c 'mkdir -p /data && echo "a note" >> /data/notes.txt && echo "notes: $(wc -l < /data/notes.txt)"'
```

```bash
docker diff notes
```

```bash
docker start -a notes
```

```bash
docker container ls -a -s --filter name=notes --format '{{.Names}}: {{.Size}}'
```

## Hands-on lab

```bash
docker run -d --name web nginx:1.30-alpine > /dev/null
sleep 2
docker diff web
```

## Break it

```bash
docker rm notes > /dev/null
docker run --rm alpine:3.23 cat /data/notes.txt 2>&1
```

## Troubleshoot it

```bash
docker container ls -a --filter name=^notes$ --format '{{.Names}}' | grep -q . || echo "no container named notes"
```

## Fix it

```bash
docker run --rm -v notes-data:/data alpine:3.23 sh -c 'echo "a note" >> /data/notes.txt'
docker run --rm -v notes-data:/data alpine:3.23 cat /data/notes.txt
```

## Practice challenge

```bash
docker run --name changes alpine:3.23 sh -c 'echo new > /tmp/new.txt; echo changed >> /etc/motd; rm /etc/issue'
docker diff changes | grep -E 'new.txt|motd|issue'
docker rm changes > /dev/null
```

## Cleanup

```bash
docker rm -f web > /dev/null
docker volume rm notes-data > /dev/null
```
