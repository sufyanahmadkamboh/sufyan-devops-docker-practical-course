<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 132 · Immutable containers · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The marketing team needs a new headline *now*, so someone edits the page inside the running container:

```bash
docker exec site sed -i 's|Welcome to the cafe|Now with breakfast|' /usr/share/nginx/html/index.html
curl -s http://localhost:8080/ | grep "<h1>"
```

It works. A week later, the container is recreated (a host restart with a new container, a deployment, a scaling
event), from the image:

```bash
docker rm -f site > /dev/null
docker run -d --name site -p 8080:80 site:1.0 > /dev/null
sleep 1
curl -s http://localhost:8080/ | grep "<h1>"
```

```text
  <h1>Welcome to the cafe</h1>
```

The headline is gone, and nobody knows why.

## Troubleshoot it

The edit lived only in the old container's writable layer. Before removing a container, `docker diff` shows such hand
changes, which is why it is the first command to run on a container you suspect has been "patched". Reproduce the
edit and look:

```bash
docker exec site sed -i 's|Welcome to the cafe|Now with breakfast|' /usr/share/nginx/html/index.html
docker diff site | grep html
```

```text
C /usr/share/nginx/html
C /usr/share/nginx/html/index.html
```

`C /usr/share/nginx/html/index.html`: the running container no longer matches its image `site:1.0`. The change is not in
Git, not in any image, not reviewed and not tested, and it disappears with the container.

## Fix it

Make the change where it belongs: in the source, then build a **new version** and replace the container.

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

```text
  <h1>Now with breakfast</h1>
0
```

The new headline survives any number of restarts, and `docker diff` finds no hand changes (`0`): the container is
exactly `site:1.1`.
