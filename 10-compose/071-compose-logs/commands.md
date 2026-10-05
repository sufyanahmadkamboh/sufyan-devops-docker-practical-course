<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 071 · Logs · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-071 examples/python-api
cp -r 10-compose/071-compose-logs/examples/. ~/docker-practice/lesson-071/
cd ~/docker-practice/lesson-071
docker compose up -d --build --quiet-build 2> /dev/null
```

## Demonstration

```bash
curl -s localhost:8080/visits > /dev/null; curl -s localhost:8080/health > /dev/null
docker compose logs --tail 2 api
```

```bash
docker compose logs -t --tail 2
```

```bash
docker compose logs --since 10s --no-log-prefix worker
```

```bash
docker compose logs -f api worker
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-071
docker compose logs --no-log-prefix api | grep -c "GET /visits"
```

## Break it

```bash
docker compose -p lesson-071-file -f broken/compose.yaml up -d 2> /dev/null
sleep 5
docker compose -p lesson-071-file -f broken/compose.yaml logs worker
echo "lines: $(docker compose -p lesson-071-file -f broken/compose.yaml logs worker | wc -l)"
```

## Troubleshoot it

```bash
docker compose -p lesson-071-file -f broken/compose.yaml exec worker ls -l /var/log/worker.log
docker compose -p lesson-071-file -f broken/compose.yaml exec worker tail -2 /var/log/worker.log
```

## Fix it

```bash
docker compose -p lesson-071-file -f broken/compose.yaml down 2> /dev/null
sed -i.bak 's# >> /var/log/worker.log##' broken/compose.yaml && rm broken/compose.yaml.bak
docker compose -p lesson-071-file -f broken/compose.yaml up -d 2> /dev/null
sleep 5
docker compose -p lesson-071-file -f broken/compose.yaml logs --no-log-prefix worker
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-071
docker compose logs -t --no-log-prefix worker | grep -E "job [0-9]*[02468] done"
```

## Cleanup

```bash
cd ~/docker-practice/lesson-071
docker compose -p lesson-071-file -f broken/compose.yaml down -v 2> /dev/null
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-071
```
