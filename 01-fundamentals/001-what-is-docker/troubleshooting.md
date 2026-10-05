<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 001 · What is Docker? · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Ask for a version that does not exist:

```bash
docker run --rm python:3.99-slim python --version 2>&1
```

```text
Unable to find image 'python:3.99-slim' locally
docker: Error response from daemon: unknown: failed to resolve reference "docker.io/library/python:3.99-slim": unexpected status from HEAD request to https://registry-1.docker.io/v2/library/python/manifests/3.99-slim: 429 Too Many Requests

Run 'docker run --help' for more information
```

## Troubleshoot it

Docker could not find the image locally (`Unable to find image … locally`) and asked the registry (Docker Hub) for
the tag `3.99-slim`. The registry answers that it does not exist: `not found` / `manifest unknown`. The container never
started; Python never ran.

You may see `429 Too Many Requests` instead: Docker Hub limits how many requests an anonymous user can make, and
answers every request with 429 until the limit resets. Either way, the message is in the last line and the image was
never downloaded (troubleshooting problem 25 covers pull failures). List
the Python images you do have:

```bash
docker image ls python
```

```text
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
python:3.14-alpine   f6a589d43c42       82.6MB           21MB        
python:3.14-slim     c3e521df8b2b        192MB         48.7MB        
```

## Fix it

Use a tag that exists (the official image's page on Docker Hub lists them):

```bash
docker run --rm python:3.14-slim python --version
```
