<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 044 · Containerizing a PHP application · solution

> Try the [challenge](challenge.md) first. The full lesson: [README.md](README.md)

## The challenge

Static files should be served by Nginx without touching PHP. Create `public/robots.txt`, give the Nginx container
read-only access to `public/` at the path its `root` points to (`/var/www/html/public`), and show that `/robots.txt`
comes back as `text/plain` from Nginx while `/` still comes from PHP.

## Solution

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

```text
Content-Type: text/plain
{"message":"Hello from PHP","hostname":"eea8870c4561","php":"8.5.11"}
```

`try_files $uri …` finds `robots.txt` in Nginx's own file system and serves it; for `/` there is no such file and the
request goes to `index.php` via FastCGI. In production, the static files are usually built into an Nginx image
instead of mounted.
