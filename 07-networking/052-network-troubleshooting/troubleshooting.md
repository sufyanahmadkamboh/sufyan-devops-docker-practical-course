<!-- generated from README.md by tools/lesson_files.py: edit README.md, not this file -->
# Lesson 052 · Network troubleshooting · troubleshooting

> The full lesson: [README.md](README.md)

## Break it

Now call it from the host, the way a user would:

```bash
code=0; curl -s -m 5 http://localhost:8080 > /dev/null || code=$?
echo "curl exit code $code"
[ "$code" -eq 0 ]
```

```text
curl exit code 52
```

And from another container on the same network:

```bash
docker run --rm --network debug-net busybox:1.37 wget -qO /dev/null -T 5 http://app:8000 2>&1
```

```text
wget: can't connect to remote host (172.18.0.2): Connection refused
```

## Troubleshoot it

Steps 1 and 2 passed: running and published. The host gets an empty reply (Docker accepted the connection on 8080
but nothing answered on the container side), and another container is refused. Step 3 and 4: what is listening inside
the container? The image has no `netstat`, so borrow BusyBox's, in the **same network namespace** as `app`:

```bash
docker run --rm --network container:app busybox:1.37 netstat -tln
```

```text
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       
tcp        0      0 127.0.0.11:41811        0.0.0.0:*               LISTEN      
tcp        0      0 127.0.0.1:8000          0.0.0.0:*               LISTEN      
```

(The `127.0.0.11:…` line is Docker's embedded DNS server, lesson 050.) `127.0.0.1:8000`: the server listens on the container's loopback interface only. Traffic forwarded from the host and
from other containers arrives on `eth0`, where nothing listens. The port is right; the **address** is wrong.

## Fix it

Make the application listen on all interfaces, `0.0.0.0` (for this server `--bind 0.0.0.0`; for Flask
`--host 0.0.0.0`, for Node `server.listen(port, "0.0.0.0")`), and recreate the container:

```bash
docker rm -f app > /dev/null
docker run -d --name app --network debug-net -p 8080:8000 python:3.14-slim python -m http.server 8000 --bind 0.0.0.0 > /dev/null
sleep 1
docker run --rm --network container:app busybox:1.37 netstat -tln | grep 8000
echo "from the host: $(curl -s -w '\n%{http_code}' http://localhost:8080 | tail -1)"
docker run --rm --network debug-net busybox:1.37 wget -qO /dev/null -T 5 http://app:8000 && echo "from a container: ok"
```

```text
tcp        0      0 0.0.0.0:8000            0.0.0.0:*               LISTEN      
from the host: 200
from a container: ok
```
