<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 132 · Immutable containers · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-132 examples/site
cp 18-production/132-immutable-containers/examples/Dockerfile ~/docker-practice/lesson-132/
cd ~/docker-practice/lesson-132
docker build -q -t site:1.0 . > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
```

## Demonstration

```bash
curl -s http://localhost:8080/ | grep "<h1>"
```

```bash
docker diff site
```

## Hands-on lab

```bash
docker inspect site --format '{{.Config.Image}} {{.Image}}'
```

## Break it

```bash
docker exec site sed -i 's|Welcome to the cafe|Now with breakfast|' /usr/share/nginx/html/index.html
curl -s http://localhost:8080/ | grep "<h1>"
```

```bash
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
```

## Troubleshoot it

```bash
docker exec site sed -i 's|Welcome to the cafe|Now with breakfast|' /usr/share/nginx/html/index.html
docker diff site | grep html
```

## Fix it

```bash
cd ~/docker-practice/lesson-132
sed 's|Welcome to the cafe|Now with breakfast|' index.html > index.new && mv index.new index.html
docker build -q -t site:1.1 . > /dev/null
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.1 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
docker diff site | grep -c html || true
```

## Practice challenge

```bash
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
```

## Cleanup

```bash
docker rm -f site > /dev/null
docker image rm -f site:1.0 site:1.1 > /dev/null
rm -rf ~/docker-practice/lesson-132
```
