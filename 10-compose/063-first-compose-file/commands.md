<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 063 · Your first Compose file · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-063 examples/python-api
cp -r 10-compose/063-first-compose-file/examples/. ~/docker-practice/lesson-063/
cd ~/docker-practice/lesson-063
ls
```

## Demonstration

```bash
cat compose.yaml
```

```bash
docker compose config --services
docker compose config | grep -E "name:|image:|target:|published:"
```

```bash
docker compose up -d --build --quiet-build 2> /dev/null
docker compose ps --format '{{.Service}}: {{.State}}  {{.Ports}}'
```

```bash
curl -s localhost:8080/visits
curl -s localhost:8080/visits
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-063
awk '{ print } /REDIS_HOST: redis/ { print "      GREETING: Hello from Compose" }' compose.yaml > compose.new
mv compose.new compose.yaml
docker compose up -d 2> /dev/null
curl -s localhost:8080/
```

## Break it

```bash
docker compose -f broken/compose.yaml config 2>&1
```

## Troubleshoot it

```bash
sed -n '2,6p' broken/compose.yaml | sed 's/ /·/g'
```

## Fix it

```bash
sed -i.bak 's/^     environment:/    environment:/' broken/compose.yaml && rm broken/compose.yaml.bak
docker compose -f broken/compose.yaml config --services
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-063
cat >> compose.yaml <<'EOF'
  cache-ui:
    image: redis:8-alpine
    command: redis-cli -h redis ping
EOF
docker compose up -d 2> /dev/null
sleep 2
docker compose logs --no-log-prefix cache-ui
```

## Cleanup

```bash
cd ~/docker-practice/lesson-063
docker compose down -v --rmi local 2> /dev/null
rm -rf ~/docker-practice/lesson-063
```
