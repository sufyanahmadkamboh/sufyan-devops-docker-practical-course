<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 009 · Container lifecycle · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
echo 'state() { docker inspect --format "{{.Name}}: {{.State.Status}} (exit code {{.State.ExitCode}})" "$@"; }' > ~/docker-practice-state.sh
echo "helper defined: run  . ~/docker-practice-state.sh  in each new terminal"
```

## Demonstration

```bash
. ~/docker-practice-state.sh
docker create --name web nginx:1.30-alpine > /dev/null; state web
docker start web > /dev/null;   state web
docker pause web > /dev/null;   state web
docker unpause web > /dev/null; state web
```

```bash
. ~/docker-practice-state.sh
docker stop web > /dev/null; state web
docker start web > /dev/null; state web
docker restart web > /dev/null; state web
```

```bash
. ~/docker-practice-state.sh
docker run -d --name sleeper alpine:3.23 sleep 300 > /dev/null
docker stop -t 2 sleeper > /dev/null; state sleeper
```

## Hands-on lab

```bash
. ~/docker-practice-state.sh
docker run -d --name cache redis:8-alpine > /dev/null
docker stop cache > /dev/null; state cache
docker start cache > /dev/null
docker rm -f cache > /dev/null && echo "cache removed"
```

## Break it

```bash
docker rm web
```

## Troubleshoot it

```bash
. ~/docker-practice-state.sh
state web
```

## Fix it

```bash
docker stop web
docker rm web
```

## Practice challenge

```bash
docker run -d --name flaky --restart on-failure:3 alpine:3.23 sh -c 'echo starting; exit 1'
```

```bash
docker inspect --format 'restarts: {{.RestartCount}}, status: {{.State.Status}}, exit code: {{.State.ExitCode}}' flaky
```

## Cleanup

```bash
docker rm -f web sleeper flaky > /dev/null 2>&1 || true
rm -f ~/docker-practice-state.sh
```
