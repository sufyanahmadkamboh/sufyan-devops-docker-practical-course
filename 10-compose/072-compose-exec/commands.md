<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 072 · exec and run · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-072 examples/python-api
cp -r 10-compose/072-compose-exec/examples/. ~/docker-practice/lesson-072/
cd ~/docker-practice/lesson-072
docker compose up -d --build --quiet-build 2> /dev/null
```

## Demonstration

```bash
docker compose exec api sh -c 'echo "hostname: $(hostname)"; echo "REDIS_HOST=$REDIS_HOST"; ls /proc | grep -c "^[0-9]" ; cat /proc/1/cmdline | tr "\0" " "; echo'
```

```bash
docker compose run --rm api sh -c 'echo "hostname: $(hostname)"; cat /proc/1/cmdline | tr "\0" " "; echo' 2> /dev/null
docker compose ps -a --format '{{.Name}}'
```

```bash
docker compose run --rm api python -c "import app; print(app.app.test_client().get('/visits').json)" 2> /dev/null
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-072
docker compose exec redis redis-cli GET visits
```

## Break it

```bash
docker compose stop api 2> /dev/null
docker compose exec api ls 2>&1
```

## Troubleshoot it

```bash
docker compose ps -a --format '{{.Service}}: {{.State}} ({{.Status}})'
```

## Fix it

```bash
docker compose run --rm --no-deps api ls 2> /dev/null
docker compose start api 2> /dev/null
docker compose exec api ls
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-072
docker compose exec -T api sh -c 'wc -l' < app.py | sed 's/$/ lines in app.py/'
```

## Cleanup

```bash
cd ~/docker-practice/lesson-072
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-072
```
