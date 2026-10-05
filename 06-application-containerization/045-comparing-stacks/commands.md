<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 045 · Comparing the stacks · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-045 examples/node-api examples/python-api examples/go-api examples/java-api examples/php-app
for pair in node:node-api python:python-api go:go-api java:java-api php:php-app; do
  cp "06-application-containerization/045-comparing-stacks/examples/${pair%%:*}/Dockerfile" ~/docker-practice/lesson-045/"${pair#*:}"/
done
cd ~/docker-practice/lesson-045
ls
```

## Demonstration

```bash
for app in node-api python-api go-api java-api php-app; do
  docker build -q -t "stack-$app:1.0" "$app" > /dev/null && echo "built stack-$app:1.0"
done
```

```bash
docker image ls --filter 'reference=stack-*' --format '{{.Repository}}\t{{.Size}}' | sort -k2 -h
```

```bash
for app in node-api python-api go-api java-api php-app; do
  docker run -d --name "stack-${app%-*}" "stack-$app:1.0" > /dev/null
done
sleep 5
docker stats --no-stream --format '{{.Name}}\t{{.MemUsage}}' | sort
```

## Hands-on lab

```bash
for app in node-api python-api go-api java-api php-app; do
  echo "$app: $(docker run --rm "stack-$app:1.0" sh -c '. /etc/os-release; echo $PRETTY_NAME')"
done
```

## Break it

```bash
sed 's/25-jdk-alpine/25-jre-alpine/' java-api/Dockerfile > java-api/Dockerfile.jre
docker build -f java-api/Dockerfile.jre -t stack-java-api:jre java-api 2>&1 | grep -E 'not found|ERROR' | head -2
test "${PIPESTATUS[0]}" -eq 0
```

## Troubleshoot it

```bash
docker run --rm eclipse-temurin:25-jre-alpine sh -c 'command -v java; command -v javac || echo "no javac in the JRE"'
```

## Fix it

```bash
rm java-api/Dockerfile.jre
docker image ls --filter 'reference=stack-java-api' --format '{{.Repository}}:{{.Tag}} {{.Size}}'
```

## Practice challenge

```bash
binary=$(docker run --rm stack-go-api:1.0 du -sk /usr/local/bin/go-api | cut -f1)
total=$(docker run --rm stack-go-api:1.0 du -skx / 2> /dev/null | cut -f1)
echo "program: $binary kB of $total kB = $((binary * 100 / total)) % of the image"
```

## Cleanup

```bash
docker rm -f stack-node stack-python stack-go stack-java stack-php > /dev/null
docker image rm -f stack-node-api:1.0 stack-python-api:1.0 stack-go-api:1.0 stack-java-api:1.0 stack-php-app:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-045
```
