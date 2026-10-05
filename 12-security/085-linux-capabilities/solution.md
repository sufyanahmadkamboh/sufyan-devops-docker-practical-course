<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 085 · Linux capabilities · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

The Python web server from lesson 084 runs as root on port 8081. Find the smallest set of capabilities it needs: start
it with `--cap-drop ALL` and check that it still answers. Then show which capabilities the server process actually has
while it runs.

## Solution

```bash
docker run -d --name py --cap-drop ALL -p 8081:8081 python:3.14-alpine python -m http.server 8081 > /dev/null && echo "started py"
```

```bash
curl -s http://localhost:8081/ | grep -o '<title>.*</title>'
```

```text
<title>Directory listing for /</title>
```

```bash
docker exec py grep CapEff /proc/1/status
```

```text
CapEff:	0000000000000000
```

The web server runs as root, yet with **no** capability at all, and it still works: most applications need none. As
root without capabilities it cannot change file owners, kill other users' processes, or bypass file permissions.
