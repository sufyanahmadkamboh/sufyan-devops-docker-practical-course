<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 002 · Why containers? · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Prove the image is self-contained: run the API's health check from the image with **no** folder mounted from your
computer.

## Solution

```bash
cd ~/docker-practice/lesson-002
docker run --rm cafe-api:1.0 python -c "import app; print(app.app.test_client().get('/health').json)"
```

```text
{'status': 'ok'}
```

Everything the application needs is inside the image: code, runtime and libraries.
