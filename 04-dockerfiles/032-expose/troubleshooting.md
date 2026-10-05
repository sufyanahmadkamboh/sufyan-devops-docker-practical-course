<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 032 · EXPOSE · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

The image is rebuilt from a copied Nginx Dockerfile, still saying `EXPOSE 80`:

```bash
sed 's/^EXPOSE 3000$/EXPOSE 80/' Dockerfile > Dockerfile.wrong
docker build -q -f Dockerfile.wrong -t cafe-api:wrong-port . > /dev/null
docker run -d --name cafe-api-wrong -P cafe-api:wrong-port > /dev/null
sleep 2
port=$(docker port cafe-api-wrong 80/tcp | head -1 | sed 's/.*://')
curl -sS "http://localhost:$port" 2>&1 || echo "no response from the application"
```

```text
curl: (52) Empty reply from server
no response from the application
```

## Troubleshoot it

The container runs and Docker published a port, yet there is no answer. Compare three things: what is published,
where the application listens, and whether it answers *inside* the container:

```bash
docker port cafe-api-wrong
docker logs cafe-api-wrong
docker exec cafe-api-wrong wget -qO- http://127.0.0.1:3000
```

```text
80/tcp -> 0.0.0.0:32785
node-api listening on port 3000
{"message":"Hello from Node.js","hostname":"8522faeb80e2","version":"dev"}
```

The application is healthy on port 3000, but `-P` published port 80, the one `EXPOSE` claimed, where nothing listens.
Docker trusts `EXPOSE`; it does not check what the application does.

## Fix it

Make `EXPOSE` match the application's port, rebuild and restart:

```bash
docker rm -f cafe-api-wrong > /dev/null
sed -i.bak 's/^EXPOSE 80$/EXPOSE 3000/' Dockerfile.wrong && rm Dockerfile.wrong.bak
docker build -q -f Dockerfile.wrong -t cafe-api:wrong-port . > /dev/null
docker run -d --name cafe-api-wrong -P cafe-api:wrong-port > /dev/null
docker port cafe-api-wrong
```

```bash
curl -s "http://localhost:$(docker port cafe-api-wrong 3000/tcp | head -1 | sed 's/.*://')"
```
