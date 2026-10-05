<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 002 · Why containers? · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-002 examples/python-api
cd ~/docker-practice/lesson-002
ls
```

## Demonstration

```bash
docker run --rm -v "$(pwd):/app" -w /app python:3.14-slim python -c "import app" 2>&1 | tail -1
test "${PIPESTATUS[0]}" -eq 0
```

```bash
printf 'FROM python:3.14-slim\nWORKDIR /app\nCOPY . .\nRUN pip install --no-cache-dir -r requirements.txt\n' > Dockerfile
docker build -q -t cafe-api:1.0 . > /dev/null
docker image ls cafe-api
```

```bash
docker run --rm cafe-api:1.0 python -c "import app; print(app.app.test_client().get('/').json)"
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-002
docker run --rm cafe-api:1.0 pip show flask | grep Version
```

## Break it

```bash
docker run --rm python:3.14-slim sh -c 'pip install -q flask==3.0.3 2>/dev/null; pip show flask | grep Version'
```

## Troubleshoot it

```bash
docker run --rm cafe-api:1.0 pip show flask | grep Version
```

## Fix it

```bash
grep -i flask requirements.txt
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-002
docker run --rm cafe-api:1.0 python -c "import app; print(app.app.test_client().get('/health').json)"
```

## Cleanup

```bash
docker image rm -f cafe-api:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-002
```
