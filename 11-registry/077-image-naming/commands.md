<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 077 · Image naming · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
docker run -d --name registry -p 5000:5000 registry:3 > /dev/null
sleep 2
docker inspect registry --format '{{.State.Status}}'
```

## Demonstration

```bash
for tag in 1.4.2 1.4 1; do docker tag busybox:1.37 localhost:5000/cafe-team/cafe-api:$tag; done
docker image ls --format '{{.Repository}}:{{.Tag}}  {{.ID}}' | grep -E "busybox|cafe-api" | sort
```

```bash
docker push -q --all-tags localhost:5000/cafe-team/cafe-api > /dev/null
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```

## Hands-on lab

```bash
docker tag localhost:5000/cafe-team/cafe-api:1.4.2 localhost:5000/cafe-team/cafe-api:sha-3f1a2b4
docker push -q localhost:5000/cafe-team/cafe-api:sha-3f1a2b4
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```

## Break it

```bash
docker tag busybox:1.37 localhost:5000/CafeTeam/CafeAPI:1.4.2 2>&1
```

## Troubleshoot it

```bash
for name in cafe-api:1.4.2-RC1 cafe_api:1.4.2 "cafe api:1.4.2" cafe-api:1.4:2; do
  docker tag busybox:1.37 "$name" 2> /dev/null && echo "valid:   $name" || echo "invalid: $name"
done
docker image rm cafe-api:1.4.2-RC1 cafe_api:1.4.2 > /dev/null
```

## Fix it

```bash
docker tag busybox:1.37 localhost:5000/cafeteam/cafe-api:1.4.2
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep cafeteam
```

## Practice challenge

```bash
docker image rm localhost:5000/cafe-team/cafe-api:1
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -c "cafe-team/cafe-api"
curl -s localhost:5000/v2/cafe-team/cafe-api/tags/list
```

## Cleanup

```bash
docker rm -f registry > /dev/null
docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -E "^localhost:5000/" | xargs docker image rm > /dev/null
```
