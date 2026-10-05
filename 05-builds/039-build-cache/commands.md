<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 039 · The build cache · commands

> Every command of the lesson, in order. The explanations: [README.md](README.md)

## Lab setup

```bash
bash scripts/lab.sh lesson-039 examples/python-api
cp 05-builds/039-build-cache/examples/Dockerfile* ~/docker-practice/lesson-039/
cd ~/docker-practice/lesson-039
ls
```

## Demonstration

```bash
docker build -t cache-api:1 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

```bash
docker build -t cache-api:1 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

```bash
sed -i.bak 's/Hello from Python/Hello from Python, version 2/' app.py && rm app.py.bak
docker build -t cache-api:2 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

## Hands-on lab

```bash
cd ~/docker-practice/lesson-039
echo "itsdangerous==2.2.0" >> requirements.txt
docker build -t cache-api:3 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'RUN pip'
```

## Break it

```bash
docker build -f Dockerfile.slow -t cache-api:slow . > /dev/null 2>&1
sed -i.bak 's/version 2/version 3/' app.py && rm app.py.bak
docker build -f Dockerfile.slow -t cache-api:slow . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)'
```

## Troubleshoot it

```bash
grep -nE '^(COPY|RUN)' Dockerfile.slow Dockerfile
```

## Fix it

```bash
docker build -t cache-api:4 . > /dev/null 2>&1
sed -i.bak 's/version 3/version 4/' app.py && rm app.py.bak
docker build -t cache-api:4 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'RUN pip'
```

## Practice challenge

```bash
cd ~/docker-practice/lesson-039
touch app.py
docker build -t cache-api:4 . 2>&1 | grep -E '^#[0-9]+ (\[[0-9]/[0-9]\]|CACHED)' | grep -A1 'COPY \. \.'
```

## Cleanup

```bash
docker image rm -f cache-api:1 cache-api:2 cache-api:3 cache-api:4 cache-api:slow > /dev/null
rm -rf ~/docker-practice/lesson-039
```
