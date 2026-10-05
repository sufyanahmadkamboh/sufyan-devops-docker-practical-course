<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 044 · Containerizing a PHP application · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-044 examples/php-app
cp 06-application-containerization/044-containerize-php/examples/Dockerfile* ~/docker-practice/lesson-044/
cd ~/docker-practice/lesson-044
ls . public
cat nginx.conf
```

## Demonstration

```bash
docker build -q -t php-app:1.0 . > /dev/null
docker image ls php-app
docker network create php-net > /dev/null
docker run -d --name php --network php-net php-app:1.0 > /dev/null
```

```bash
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
docker ps --format '{{.Names}}: {{.Image}} {{.Status}}'
```

```bash
curl -s http://localhost:8088/
```

## Hands-on lab

```bash
docker exec php ps -o user,args
```

## Break it

```bash
docker rm -f php web > /dev/null
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
```

```bash
docker ps -a --filter name=web --format '{{.Names}}: {{.Status}}'
```

## Troubleshoot it

```bash
docker logs web 2>&1 | grep emerg
```

```bash
docker network inspect php-net --format '{{range .Containers}}{{.Name}} {{end}}'
```

## Fix it

```bash
docker rm -f web > /dev/null
docker run -d --name php --network php-net php-app:1.0 > /dev/null
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 2
curl -s http://localhost:8088/
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-044
printf 'User-agent: *\nDisallow:\n' > public/robots.txt
docker rm -f web > /dev/null
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
  -v "$(pwd)/public:/var/www/html/public:ro" nginx:1.30-alpine > /dev/null
sleep 2
curl -sI http://localhost:8088/robots.txt | grep -i '^content-type'
curl -s http://localhost:8088/
```

## Real-world example

```bash
cat Dockerfile.laravel
```

## Cleanup

```bash
docker rm -f web php > /dev/null
docker network rm php-net > /dev/null
docker image rm -f php-app:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-044
```
