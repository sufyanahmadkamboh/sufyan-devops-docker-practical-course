<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 062 · Why Docker Compose? · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Stop and remove the whole Compose application with one command, then prove nothing of the project is left (no
containers, no network).

## Solution

```bash
cd ~/docker-practice/lesson-062
docker compose down 2>&1 | grep -c Removed
[ -z "$(docker ps -aq --filter label=com.docker.compose.project=lesson-062)" ] && \
  [ -z "$(docker network ls -q --filter name=lesson-062)" ] && echo "nothing left"
```

```text
3
nothing left
```

`down` removed both containers and the network. Compose finds its objects through labels it sets on them
(`com.docker.compose.project`); lesson 101 covers labels.
