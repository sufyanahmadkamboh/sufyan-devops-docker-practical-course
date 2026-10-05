<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 074 · up, down and the project lifecycle · hands-on lab

> The full lesson: [README.md](README.md)

## Hands-on lab

**Instructions.** Make `down` remove everything the project created except the pulled `redis` and `alpine` images:
containers, network, the volume and the built `api` image. Then verify that nothing of the project is left.

**Expected result.** No container, network or volume named `lesson-074…`, and no image `lesson-074-api`.

**Verification.**

```bash
cd ~/docker-practice/lesson-074
docker compose down -v --rmi local 2> /dev/null
echo "$(docker ps -aq --filter name=lesson-074 | wc -l) $(docker network ls -q --filter name=lesson-074 | wc -l) $(docker volume ls -q --filter name=lesson-074 | wc -l) $(docker image ls -q lesson-074-api | wc -l)" | tr -s ' '
```

Start it again for the next steps:

```bash
docker compose up -d --build --quiet-build 2> /dev/null
```
