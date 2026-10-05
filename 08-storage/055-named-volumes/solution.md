<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 055 · Named volumes · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Back up a volume: create a volume `menu` with a file in it, then write its contents into a `menu.tar` archive in a lab
folder on your computer, using a temporary container that mounts both the volume and the folder.

## Solution

```bash
mkdir -p ~/docker-practice/lesson-055 && cd ~/docker-practice/lesson-055
docker run --rm -v menu:/data alpine:3.23 sh -c 'echo "espresso 2.50" > /data/menu.txt'
docker run --rm -v menu:/data:ro -v "$(pwd):/backup" alpine:3.23 tar -cf /backup/menu.tar -C /data .
tar -tf menu.tar
```

```text
./
./menu.txt
```

The same pattern restores it (`tar -xf /backup/menu.tar -C /data` into a new volume). Lesson 058 backs up a real
database.
