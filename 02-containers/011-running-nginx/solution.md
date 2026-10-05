<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 011 · Running Nginx · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Check that Nginx serves `styles.css` with the right content type. Then stop `web`, start it again, and check whether the
website is still there. Explain the result.

## Solution

```bash
curl -sI http://localhost:8080/styles.css | grep -i '^content-type'
```

```text
Content-Type: text/css
```

```bash
docker stop web > /dev/null && docker start web > /dev/null
curl -s http://localhost:8080 | grep '<h1>'
```

```text
  <h1>Welcome to the cafe</h1>
```

The website survives stop and start: the files are in the container's writable layer, which lives as long as the
container. Only removing the container (or creating a new one) loses them.
