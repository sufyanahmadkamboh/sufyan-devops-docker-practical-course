<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 075 · What is a registry? · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A teammate pulls the version they expect to be there:

```bash
docker pull localhost:5000/cafe/alpine:3.24 2>&1
```

```text
Error response from daemon: failed to resolve reference "localhost:5000/cafe/alpine:3.24": localhost:5000/cafe/alpine:3.24: not found
```

## Troubleshoot it

`manifest unknown`: the registry answered (so address, network and authentication are fine), but it has no image with
that tag. Ask the registry which tags exist:

```bash
curl -s localhost:5000/v2/cafe/alpine/tags/list
```

```text
{"name":"cafe/alpine","tags":["3.23"]}
```

The tag was never pushed. Other answers mean other problems: `connection refused` or a timeout (wrong address, registry
down), `unauthorized` (lesson 078), `429 Too Many Requests` (a rate limit, troubleshooting problem 25).

## Fix it

Pull a tag that exists, or push the missing one first:

```bash
docker pull -q localhost:5000/cafe/alpine:3.23
```
