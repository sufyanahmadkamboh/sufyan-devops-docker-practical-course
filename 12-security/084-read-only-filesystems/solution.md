<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 084 · Read-only file systems · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Run the Python built-in web server (`python -m http.server 8081`) from `python:3.14-alpine` with a read-only root
file system, serving files from a tmpfs at `/srv`. Write a file into `/srv` with `docker exec`, then fetch it with
`curl`.

## Solution

```bash
docker run -d --name py-ro --read-only --tmpfs /srv -w /srv -p 8081:8081 python:3.14-alpine python -m http.server 8081 > /dev/null && echo "started py-ro"
```

```bash
docker exec py-ro sh -c 'echo "hello from tmpfs" > /srv/hello.txt'
curl -s http://localhost:8081/hello.txt
```

```text
hello from tmpfs
```

Python does not need to write anywhere else, so `/srv` is the only writable folder. Anything written there disappears
when the container stops: that is what you want for scratch data.
