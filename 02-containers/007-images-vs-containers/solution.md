<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 007 · Images vs containers · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Prove that one image can run several containers **at the same time**: start three `alpine:3.23` containers in the
background running `sleep 300`, show that all three are running from the same image ID, then remove them.

## Solution

```bash
for n in one two three; do docker run -d --name "sleep-$n" alpine:3.23 sleep 300 > /dev/null; done
docker ps --filter name=sleep- --format '{{.Names}} {{.Image}}'
echo "$(docker ps -q --filter ancestor=alpine:3.23 | wc -l | tr -d ' ') running"
docker inspect --format '{{.Image}}' sleep-one sleep-two sleep-three | sort -u | wc -l | tr -d ' '
docker rm -f sleep-one sleep-two sleep-three > /dev/null
```

```text
sleep-three alpine:3.23
sleep-two alpine:3.23
sleep-one alpine:3.23
3 running
1
```

The last number is `1`: one image ID behind three containers. `-d` starts a container in the background (lesson 009).
