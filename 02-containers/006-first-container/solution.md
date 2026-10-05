<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 006 · Your first container · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Run `hello-world` twice **without** `--rm`, count how many `hello-world` containers exist, then remove exactly those
containers with one command.

## Solution

```bash
docker run hello-world > /dev/null
docker run hello-world > /dev/null
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
docker rm $(docker ps -aq --filter ancestor=hello-world) > /dev/null && echo "removed"
echo "hello-world containers: $(docker ps -aq --filter ancestor=hello-world | wc -l | tr -d ' ')"
```

```text
hello-world containers: 3
removed
hello-world containers: 0
```

Three, not two: the container from the Demonstration is still there. Every `docker run` without `--rm` creates a new
container; stopped containers pile up until you remove them. `-q` prints only IDs, which is what `docker rm` expects.
