# Lesson 044 · Containerizing a PHP application

> Level 7 · Application containerization · ⏱ 30 minutes · run every command from the course folder

## What are we learning?

A PHP application usually runs as **two** containers: **PHP-FPM**, which executes PHP code and speaks the FastCGI
protocol on port 9000, and **Nginx**, which receives HTTP requests, serves static files itself and forwards `.php`
requests to PHP-FPM. Each container does one job, the PHP image contains the code, and the two find each other by name
on a shared network. This is also how Laravel and Symfony applications are deployed.

## Visual

```text
  browser / curl                     network php-net (a user-defined network: lesson 048)
       │  http://localhost:8088      ┌──────────────────────────────────────────────────────────────┐
       ▼                             │                                                              │
  -p 8088:8080 ─────────────────────▶│  web  (nginx:1.30-alpine)            php  (php-app:1.0)       │
                                     │  listen 8080                         php-fpm  :9000           │
                                     │  /robots.txt, *.css  → served by Nginx                       │
                                     │  everything else ── FastCGI ─────▶ fastcgi_pass php:9000      │
                                     │                                     runs public/index.php    │
                                     └──────────────────────────────────────────────────────────────┘
  nginx.conf: fastcgi_pass php:9000   "php" = the PHP container's name, resolved by Docker's DNS (lesson 050)
```

## Lab setup

<!-- test: contains=lab ready -->
```bash
bash scripts/lab.sh lesson-044 examples/php-app
cp 06-application-containerization/044-containerize-php/examples/Dockerfile* ~/docker-practice/lesson-044/
cd ~/docker-practice/lesson-044
ls . public
cat nginx.conf
```

## Demonstration

Build the PHP image, create a network, and start PHP-FPM under the name `php` (the name `nginx.conf` uses):

<!-- test: contains=php-app; output -->
```bash
docker build -q -t php-app:1.0 . > /dev/null
docker image ls php-app
docker network create php-net > /dev/null
docker run -d --name php --network php-net php-app:1.0 > /dev/null
```

```text
IMAGE         ID             DISK USAGE   CONTENT SIZE   EXTRA
php-app:1.0   5e278214849c        150MB         38.8MB        
```

Start Nginx on the same network with the configuration mounted read-only (`:ro`) as its default site:

<!-- test: contains=web -->
```bash
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
docker ps --format '{{.Names}}: {{.Image}} {{.Status}}'
```

<!-- test: retry=10; contains=Hello from PHP; output -->
```bash
curl -s http://localhost:8088/
```

```text
{"message":"Hello from PHP","hostname":"904b1663728e","php":"8.5.11"}
```

The `hostname` is the **PHP** container's ID: Nginx received the request, PHP-FPM ran the code.

## Command breakdown

| Command / setting | Meaning |
|---|---|
| `FROM php:8.5-fpm-alpine` | the official PHP image, FPM variant (no web server inside) |
| `php.ini-production` → `php.ini` | the image ships recommended production settings; activate them |
| `docker network create php-net` | a network on which containers find each other by name |
| `--name php --network php-net` | the PHP container is reachable as `php` from that network |
| `-v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro"` | replace Nginx's default site with ours, read-only |
| `fastcgi_pass php:9000` | forward PHP requests to host `php`, port 9000, using FastCGI |

## Hands-on lab

**Instructions.** Look at the processes in the PHP container. Which user runs the FPM **master**, and which user runs
the **workers** that execute your code?

**Expected result.** `php-fpm: master process` runs as `root`, the `php-fpm: pool www` workers as `www-data`.

**Verification.**

<!-- test: contains=pool www; contains=www-data -->
```bash
docker exec php ps -o user,args
```

## Break it

The PHP container crashes and is removed while Nginx gets restarted, a common situation during a deployment:

<!-- test -->
```bash
docker rm -f php web > /dev/null
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
```

It starts, and a few seconds later:

<!-- test: retry=10; contains=Exited; output -->
```bash
docker ps -a --filter name=web --format '{{.Names}}: {{.Status}}'
```

```text
web: Exited (1) 4 seconds ago
```

## Troubleshoot it

Nginx itself exited. Its log says why:

<!-- test: contains=host not found in upstream; output -->
```bash
docker logs web 2>&1 | grep emerg
```

```text
2026/10/05 17:07:08 [emerg] 1#1: host not found in upstream "php" in /etc/nginx/conf.d/default.conf:8
nginx: [emerg] host not found in upstream "php" in /etc/nginx/conf.d/default.conf:8
```

`host not found in upstream "php"`: Nginx resolves the host names in `fastcgi_pass` **when it starts**. No container
named `php` exists on `php-net`, Docker's DNS has no answer (after a few seconds of trying, which is why the container
was `Up` at first), and Nginx refuses to start with an invalid configuration.
Check what is on the network:

<!-- test: absent=php -->
```bash
docker network inspect php-net --format '{{range .Containers}}{{.Name}} {{end}}'
```

## Fix it

Start the backend first, then the proxy (Docker Compose expresses this order with `depends_on`, lesson 068):

<!-- test: contains=Hello from PHP -->
```bash
docker rm -f web > /dev/null
docker run -d --name php --network php-net php-app:1.0 > /dev/null
docker run -d --name web --network php-net -p 8088:8080 \
  -v "$(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro" nginx:1.30-alpine > /dev/null
sleep 2
curl -s http://localhost:8088/
```

## Practice challenge

Static files should be served by Nginx without touching PHP. Create `public/robots.txt`, give the Nginx container
read-only access to `public/` at the path its `root` points to (`/var/www/html/public`), and show that `/robots.txt`
comes back as `text/plain` from Nginx while `/` still comes from PHP.

<details>
<summary>Solution</summary>

<!-- test: contains=Content-Type: text/plain; contains=Hello from PHP; output -->
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

</details>

## Real-world example

A Laravel application uses exactly this layout: an Nginx container and a PHP-FPM image that contains the code and its
Composer dependencies. The PHP image adds the extensions the application needs (`docker-php-ext-install pdo_mysql`),
installs dependencies with Composer in a separate build stage, makes only `storage/` and `bootstrap/cache/` writable,
and takes its configuration (`APP_KEY`, `DB_HOST`) from environment variables instead of a `.env` file in the image.
The course's annotated example (not built here; multi-stage builds are lesson 087):

<!-- test: contains=docker-php-ext-install -->
```bash
cat Dockerfile.laravel
```

## Recap

- PHP runs as PHP-FPM (FastCGI, port 9000) behind Nginx (HTTP): two containers, one job each.
- The PHP image contains the code; Nginx reaches it by container name on a shared network.
- Nginx resolves `fastcgi_pass` hosts at start-up: `host not found in upstream` means the backend is not on the network.
- Static files are served by Nginx; everything else goes to PHP-FPM.

## Cleanup

<!-- test -->
```bash
docker rm -f web php > /dev/null
docker network rm php-net > /dev/null
docker image rm -f php-app:1.0 > /dev/null
rm -rf ~/docker-practice/lesson-044
```

Next: [Lesson 045 · Comparing the stacks](../045-comparing-stacks/README.md)
