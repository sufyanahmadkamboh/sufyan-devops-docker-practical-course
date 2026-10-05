<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 006 · Your first container · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

A typo in the image name:

```bash
docker run hello-word 2>&1
```

```text
Unable to find image 'hello-word:latest' locally
docker: Error response from daemon: pull access denied for hello-word, repository does not exist or may require 'docker login'

Run 'docker run --help' for more information
```

## Troubleshoot it

Read the steps again. Step 1 failed silently (no local image `hello-word`), so Docker went to step 2 and asked Docker
Hub for the repository `library/hello-word`. The answer:

- `pull access denied for hello-word, repository does not exist or may require 'docker login'`: there is no public
  repository of that name. Docker cannot tell "does not exist" from "private", so it mentions `docker login`; that is
  misleading here, the name is simply wrong.
- `429 Too Many Requests`: Docker Hub refused because of its rate limit, before even checking the name
  (troubleshooting problem 25).
- `…: not found`: the same answer, worded by a registry mirror. Engines configured with a Docker Hub mirror (CI
  machines, many company networks) ask the mirror first, and it reports a missing repository this way.

Either way no container was created. Compare with the images you actually have:

```bash
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep hello
```

## Fix it

Use the correct name:

```bash
docker run --rm hello-world | grep "Hello from Docker"
```
