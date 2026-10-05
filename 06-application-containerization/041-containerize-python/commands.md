<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 041 · Containerizing a Python application · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-041 examples/python-api
cp -r 06-application-containerization/041-containerize-python/examples/. ~/docker-practice/lesson-041/
cd ~/docker-practice/lesson-041
cat Dockerfile
```

## Demonstration

```bash
docker build -q -t python-api:1.0 . > /dev/null
docker image ls python-api
docker run -d --name python-api -p 8082:5000 python-api:1.0 > /dev/null
```

```bash
curl -s http://localhost:8082/
```

```bash
docker logs python-api 2>&1 | head -2
```

## Hands-on lab

```bash
docker top python-api -o pid,user,args
```

## Break it

```bash
docker run -d --name python-dev -p 8083:5000 python-api:1.0 flask --app app run > /dev/null
sleep 3
curl -sS http://localhost:8083/ 2>&1
```

## Troubleshoot it

```bash
docker logs python-dev 2>&1 | grep Running
```

```bash
docker exec python-dev python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/').read().decode())"
```

## Fix it

```bash
docker rm -f python-dev > /dev/null
docker run -d --name python-dev -p 8083:5000 python-api:1.0 flask --app app run --host 0.0.0.0 > /dev/null
sleep 3
curl -s http://localhost:8083/
```

## Practice challenge

```bash
docker run -d --name python-4w -p 8084:5000 -e GUNICORN_CMD_ARGS="--workers 4" python-api:1.0 > /dev/null
sleep 3
echo "with GUNICORN_CMD_ARGS: $(docker top python-4w | grep -c gunicorn) gunicorn processes"
docker rm -f python-4w > /dev/null
docker run -d --name python-4w -p 8084:5000 python-api:1.0 gunicorn --bind 0.0.0.0:5000 --workers 4 app:app > /dev/null
sleep 3
echo "with a new command: $(docker top python-4w | grep -c gunicorn) gunicorn processes"
```

## Cleanup

```bash
docker rm -f python-api python-dev python-4w > /dev/null 2>&1 || true
docker image rm -f python-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-041
```
