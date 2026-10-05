<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 057 · Volumes vs bind mounts · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-057
cd ~/docker-practice/lesson-057
mkdir empty-folder
```

## Demonstration

```bash
docker run -d --name with-volume -p 8080:80 -v web-root:/usr/share/nginx/html nginx:1.30-alpine > /dev/null
curl -s http://localhost:8080 | grep -o '<title>.*</title>'
docker run --rm -v web-root:/data alpine:3.23 ls /data
```

## Hands-on lab

```bash
docker inspect with-volume --format '{{range .Mounts}}{{.Type}} {{.Source}}{{end}}'
```

## Break it

```bash
docker run -d --name with-bind -p 8081:80 -v "$(pwd)/empty-folder:/usr/share/nginx/html" nginx:1.30-alpine > /dev/null
sleep 1
curl -s -w '\nHTTP %{http_code}\n' http://localhost:8081 | tail -1
```

## Troubleshoot it

```bash
echo "files: [$(docker exec with-bind ls /usr/share/nginx/html)]"
docker logs with-bind 2>&1 | grep -m1 'directory index'
```

## Fix it

```bash
echo '<h1>Served from the host</h1>' > empty-folder/index.html
curl -s -w '\nHTTP %{http_code}\n' http://localhost:8081 | tail -1
```

## Practice challenge

```bash
docker run -d --name scratch --mount type=tmpfs,target=/scratch,tmpfs-size=16m alpine:3.23 sleep 300 > /dev/null
docker exec scratch sh -c 'grep " /scratch " /proc/mounts; echo temp > /scratch/file.txt'
docker restart scratch > /dev/null
echo "after restart: [$(docker exec scratch ls /scratch)]"
```

## Cleanup

```bash
docker rm -f with-volume with-bind scratch > /dev/null
docker volume rm web-root > /dev/null
rm -rf ~/docker-practice/lesson-057
```
