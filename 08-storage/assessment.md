# Module 08 assessment · Storage

> Lessons [053](053-writable-layer/README.md)–[058](058-persistent-database/README.md) · ⏱ 40 minutes · try every
> question before opening its answer

## Knowledge check

**1. A container writes a file to `/tmp`, is stopped and started again. Is the file still there? And after
`docker rm` and a new `docker run`?**

<details><summary>Answer</summary>

After stop and start: yes, the writable layer belongs to the container. After `docker rm`: no, the writable layer is
deleted with the container, and the new container starts from the image (lesson 053).

</details>

**2. What does `-v data:/app/data` create, and what does `-v "$(pwd)/data:/app/data"` create?**

<details><summary>Answer</summary>

The first is a **named volume** called `data`; the second a **bind mount** of the host folder. A source without a
`/` is always a volume name (lesson 054).

</details>

**3. You mount an empty named volume, and separately an empty host folder, over a path where the image has files. What
does the container see in each case?**

<details><summary>Answer</summary>

The empty volume is first filled with the image's files (copy-up), so the container sees them. The bind mount shows
the empty host folder and hides the image's files (lesson 057).

</details>

**4. `docker volume rm app-data` answers `volume is in use`. How do you find out by what?**

<details><summary>Answer</summary>

`docker ps -a --filter volume=app-data`: running **and stopped** containers that reference it (lesson 055).

</details>

**5. What is a dangling volume, and why look inside before pruning?**

<details><summary>Answer</summary>

A volume no container references. Anonymous volumes of removed containers become dangling, and they may hold data
someone believes is lost (lesson 056).

</details>

**6. Where must a Postgres 18 image's named volume be mounted?**

<details><summary>Answer</summary>

At `/var/lib/postgresql`, the path the image declares as its `VOLUME` (the data itself lives in
`/var/lib/postgresql/18/docker`). Check it with `docker image inspect IMAGE --format '{{json .Config.Volumes}}'`
(lesson 058).

</details>

**7. When is tmpfs the right choice?**

<details><summary>Answer</summary>

For data that must never touch the disk or need not survive the container: scratch files, caches, decrypted secrets,
the writable `/tmp` of a read-only container (lessons 057, 084).

</details>

## Practical task

Create a named volume `exam-notes`, write the line `exam passed` into `/data/result.txt` from one container, read it
from a second container started from a **different** image, then back the volume up into `exam-notes.tar` in a lab
folder.

<details><summary>Solution</summary>

<!-- test: contains=exam passed; contains=result.txt; output -->
```bash
mkdir -p ~/docker-practice/assessment-08 && cd ~/docker-practice/assessment-08
docker run --rm -v exam-notes:/data alpine:3.23 sh -c 'echo "exam passed" > /data/result.txt'
docker run --rm -v exam-notes:/data:ro busybox:1.37 cat /data/result.txt
docker run --rm -v exam-notes:/data:ro -v "$(pwd):/backup" alpine:3.23 tar -cf /backup/exam-notes.tar -C /data .
tar -tf exam-notes.tar
```

```text
exam passed
./
./result.txt
```

</details>

## Troubleshooting task

Set up the broken system: a site that should show the team's page, but does not.

<!-- test: contains=Welcome to nginx; retry=5 -->
```bash
mkdir -p ~/docker-practice/assessment-08/team-site && cd ~/docker-practice/assessment-08
echo '<h1>Team page</h1>' > team-site/index.html
docker run -d --name team -p 8090:80 -v team-site:/usr/share/nginx/html nginx:1.30-alpine > /dev/null
sleep 1
curl -s http://localhost:8090 | grep -o '<title>.*</title>'
```

Explain the evidence, fix it, and prove the team's page is served.

<details><summary>Solution</summary>

The mount is a named volume called `team-site`, filled with nginx's default page, not the host folder:

<!-- test: contains=volume; output -->
```bash
docker inspect team --format '{{range .Mounts}}{{.Type}} {{.Name}} -> {{.Destination}}{{end}}'
```

```text
volume team-site -> /usr/share/nginx/html
```

<!-- test: contains=Team page; retry=5 -->
```bash
cd ~/docker-practice/assessment-08
docker rm -f team > /dev/null
docker volume rm team-site > /dev/null
docker run -d --name team -p 8090:80 -v "$(pwd)/team-site:/usr/share/nginx/html:ro" nginx:1.30-alpine > /dev/null
sleep 1
curl -s http://localhost:8090
```

</details>

## Real-world scenario

A small company runs its ticket system and its Postgres database in containers on one server. An administrator
applied a security update with `docker rm -f db && docker run -d --name db -e POSTGRES_PASSWORD_FILE=… postgres:18-alpine`,
the same command that created the database a year ago, and the ticket system is now empty. Where is the data
probably, how do you check, and what should change?

<details><summary>Model answer</summary>

First, stop and do not prune anything. The command has no `-v`, so the old container stored its data in an
**anonymous** volume (the image declares `VOLUME /var/lib/postgresql`). `docker rm -f` without `-v` kept that volume;
it is now dangling, and the new container got a new, empty one (lesson 056). List
`docker volume ls --filter dangling=true`, look inside each candidate with a temporary container for
`18/docker/PG_VERSION`, and copy the data into a named volume (or start the database with that volume mounted at
`/var/lib/postgresql`). For the future: a named volume at the path the image declares, a `pg_dump` before every
update, and a tested restore (lesson 058).

</details>

## Cleanup

<!-- test -->
```bash
docker rm -f team > /dev/null
docker volume rm exam-notes > /dev/null
rm -rf ~/docker-practice/assessment-08
```
