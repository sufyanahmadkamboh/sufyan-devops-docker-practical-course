<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 022 · Your first Dockerfile · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A typing error in an instruction:

```bash
printf 'FROM nginx:1.30-alpine\nCOPPY . /usr/share/nginx/html/\n' > Dockerfile.broken
docker build -f Dockerfile.broken -t cafe-site:broken . 2>&1 | grep -E '>>>|ERROR'
```

```text
   2 | >>> COPPY . /usr/share/nginx/html/
ERROR: failed to build: failed to solve: dockerfile parse error on line 2: unknown instruction: COPPY (did you mean COPY?)
```

## Troubleshoot it

`dockerfile parse error on line 2: unknown instruction: COPPY`: the build stopped before running anything, while
**reading** the Dockerfile. The `>>>` marks the line, and Docker even suggests the fix. Read build errors from the
`ERROR:` line upwards: the line number, then the failing instruction. No image was created:

```bash
docker image inspect cafe-site:broken > /dev/null 2>&1 || echo "no image cafe-site:broken"
```

## Fix it

```bash
sed -i.bak 's/^COPPY/COPY/' Dockerfile.broken && rm Dockerfile.broken.bak
docker build -q -f Dockerfile.broken -t cafe-site:fixed . > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' cafe-site
```
